# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Tuple, List, Optional

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
import os

from memmer.generated.pain import (
    DirectDebitTransactionInformation9,
    PaymentIdentification1,
    ActiveOrHistoricCurrencyAndAmount,
    DirectDebitTransaction6,
    MandateRelatedInformation6,
    AccountIdentification4Choice,
    CashAccount16,
    PartyIdentification32,
    BranchAndFinancialInstitutionIdentification4,
    FinancialInstitutionIdentification7,
    RemittanceInformation5,
    GroupHeader39,
    PaymentTypeInformation20,
    ServiceLevel8Choice,
    LocalInstrument2Choice,
    SequenceType1Code,
    Party6Choice,
    PersonIdentification5,
    GenericPersonIdentification1,
    GenericFinancialIdentification1,
    PersonIdentificationSchemeName1Choice,
    PaymentInstructionInformation4,
    PaymentMethod2Code,
    ChargeBearerType1Code,
    CustomerDirectDebitInitiationV02,
    Document,
)
from memmer.generated.pain import __NAMESPACE__
from memmer.orm import Member, Setting, Tally
from .fees import compute_total_fee
from .maintenance import archive_onetimecosts

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from xsdata.models.datatype import XmlDateTime, XmlDate
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from unidecode import unidecode


@dataclass
class CreditorInfo:
    name: str
    iban: str
    bic: str
    identification: str


@dataclass
class Asset:
    debitor: Member
    purpose: str
    amount: Decimal
    e2e_id: str


def sanitize(string: str) -> str:
    # This needs to be done manually as unidecode doesn't want to use German transliteration rules as those letters
    # are also used outside of German. However, we assume German names and thus use German rules.
    string = string.replace("ä", "ae")
    string = string.replace("ö", "oe")
    string = string.replace("ü", "ue")

    return unidecode(string)


def to_sepa_transactions(
    assets: List[Asset],
) -> Tuple[Decimal, List[DirectDebitTransactionInformation9]]:
    transactions = []
    total = Decimal(0)

    for asset in assets:
        assert asset.amount >= 0
        if asset.amount == 0:
            continue

        total += asset.amount

        e2e_id = asset.e2e_id.format(mem_id=asset.debitor.id)

        mandate_signed = asset.debitor.sepa_mandate_date
        assert mandate_signed != None

        if (
            not asset.debitor.account_owner is None
            and len(asset.debitor.account_owner) > 0
        ):
            account_owner = asset.debitor.account_owner
        else:
            # Shouldn't happen, but as a fallback we can always use the member's name
            account_owner = "{} {}".format(
                asset.debitor.first_name, asset.debitor.last_name
            )

        account_owner = sanitize(account_owner)
        member_name = sanitize(
            "{}, {}".format(asset.debitor.last_name, asset.debitor.first_name)
        )

        transactions.append(
            DirectDebitTransactionInformation9(
                pmt_id=PaymentIdentification1(end_to_end_id=e2e_id),
                instd_amt=ActiveOrHistoricCurrencyAndAmount(
                    ccy="EUR", value="{:.2f}".format(asset.amount)  # type: ignore
                ),
                drct_dbt_tx=DirectDebitTransaction6(
                    mndt_rltd_inf=MandateRelatedInformation6(
                        # We reuse the member ID as the SEPA mandate ID
                        mndt_id=str(asset.debitor.id),
                        dt_of_sgntr=XmlDate(
                            year=mandate_signed.year,
                            month=mandate_signed.month,
                            day=mandate_signed.day,
                        ),
                        amdmnt_ind=False,
                    )
                ),
                dbtr_agt=BranchAndFinancialInstitutionIdentification4(
                    fin_instn_id=FinancialInstitutionIdentification7(
                        othr=GenericFinancialIdentification1(id="NOTPROVIDED")
                    )
                ),
                dbtr=PartyIdentification32(nm=account_owner),
                dbtr_acct=CashAccount16(
                    id=AccountIdentification4Choice(iban=asset.debitor.iban)
                ),
                ultmt_dbtr=PartyIdentification32(nm=member_name),
                rmt_inf=RemittanceInformation5(ustrd=[asset.purpose]),
            )
        )

    return (total, transactions)


def assemble_monthly_fee_assets(
    session: Session, collection_date: date, clear_onetimecosts: bool = True
) -> List[Asset]:
    # TODO: Restrict to those members that actually have to pay anything
    # i.e. active ones and ones with open onetime fees
    members = session.scalars(
        select(Member)
        .where(Member.sepa_mandate_date != None)
        .order_by(Member.id.asc())
        # Eager load these associations as they are needed anyway
        .options(joinedload(Member.participating_sessions))
        .options(joinedload(Member.trained_sessions))
        .options(joinedload(Member.one_time_fees))
    ).unique()

    e2e_id_template = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_E2E_ID_TEMPLATE)
    ).one()
    purpose = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_PURPOSE)
    ).one()

    assets: List[Asset] = []

    for current_member in members:
        fee = compute_total_fee(
            session=session, member=current_member, target_date=collection_date
        )

        if fee > 0:
            if clear_onetimecosts:
                archive_onetimecosts(session=session, member=current_member)

            assets.append(
                Asset(
                    debitor=current_member,
                    purpose=purpose,
                    amount=fee,
                    e2e_id=e2e_id_template,
                )
            )

    return assets


def create_sepa_payment_initiation_message_object(
    session: Session,
    msg_id: str,
    creditor_info: CreditorInfo,
    collection_date: date,
    assets: List[Asset],
) -> Document:
    now = datetime.now()

    e2e_id_template = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_E2E_ID_TEMPLATE)
    ).one()
    purpose = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_PURPOSE)
    ).one()

    total_sum, transactions = to_sepa_transactions(assets=assets)

    group_header = GroupHeader39(
        msg_id=msg_id,
        cre_dt_tm=XmlDateTime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            second=now.second,
            fractional_second=0,
            offset=0,
        ),
        nb_of_txs=str(len(transactions)),
        ctrl_sum="{:.2f}".format(total_sum),  # type: ignore
        initg_pty=PartyIdentification32(nm=sanitize(creditor_info.name)),
    )

    payment_type = PaymentTypeInformation20(
        svc_lvl=ServiceLevel8Choice(cd="SEPA"),
        lcl_instrm=LocalInstrument2Choice(cd="CORE"),
        seq_tp=SequenceType1Code.RCUR,
    )
    creditor = PartyIdentification32(nm=sanitize(creditor_info.name))
    creditor_account = CashAccount16(
        id=AccountIdentification4Choice(iban=creditor_info.iban)
    )
    creditor_agent = BranchAndFinancialInstitutionIdentification4(
        fin_instn_id=FinancialInstitutionIdentification7(bic=creditor_info.bic)
    )
    creditor_scheme_id = PartyIdentification32(
        id=Party6Choice(
            prvt_id=PersonIdentification5(
                othr=[
                    GenericPersonIdentification1(
                        id=creditor_info.identification,
                        schme_nm=PersonIdentificationSchemeName1Choice(prtry="SEPA"),
                    )
                ]
            )
        )
    )

    payment_information = PaymentInstructionInformation4(
        pmt_inf_id=msg_id,
        pmt_mtd=PaymentMethod2Code.DD,
        btch_bookg=True,
        nb_of_txs=str(len(transactions)),
        ctrl_sum="{:.2f}".format(total_sum),  # type: ignore
        pmt_tp_inf=payment_type,
        reqd_colltn_dt=XmlDate(
            year=collection_date.year,
            month=collection_date.month,
            day=collection_date.day,
        ),
        cdtr=creditor,
        cdtr_acct=creditor_account,
        cdtr_agt=creditor_agent,
        chrg_br=ChargeBearerType1Code.SLEV,
        cdtr_schme_id=creditor_scheme_id,
        drct_dbt_tx_inf=transactions,
    )

    init = CustomerDirectDebitInitiationV02(
        grp_hdr=group_header,
        pmt_inf=[payment_information],
    )

    return Document(cstmr_drct_dbt_initn=init)


def serialize_sepa_message(doc: Document) -> str:
    namespace = __NAMESPACE__
    config = SerializerConfig(
        pretty_print=True, schema_location=namespace + " pain.008.001.02.xsd"
    )
    serializer = XmlSerializer(config=config)
    return serializer.render(doc, ns_map={None: namespace})


def create_tally(
    session: Session,
    output_dir: str,
    collection_date: date,
    assets: Optional[List[Asset]] = None,
):
    creditor_name = (
        session.scalars(
            select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_NAME)
        )
        .one()
        .value
    )
    creditor_iban = (
        session.scalars(
            select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_IBAN)
        )
        .one()
        .value
    )
    creditor_bic = (
        session.scalars(
            select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_BIC)
        )
        .one()
        .value
    )
    creditor_id = (
        session.scalars(
            select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_ID)
        )
        .one()
        .value
    )

    now = datetime.now()
    message_id = "Memmer-{}-{:02d}-{:02d}-{:02d}".format(
        now.date().isoformat(), now.hour, now.minute, now.second
    )

    if assets is None:
        # Assume that we want to create a regular monthly tally
        assets = assemble_monthly_fee_assets(
            session=session, collection_date=collection_date, clear_onetimecosts=True
        )

    message = create_sepa_payment_initiation_message_object(
        session=session,
        msg_id=message_id,
        creditor_info=CreditorInfo(
            name=creditor_name,
            iban=creditor_iban,
            bic=creditor_bic,
            identification=creditor_id,
        ),
        collection_date=collection_date,
        assets=assets,
    )

    serialized_message = serialize_sepa_message(message)

    with open(os.path.join(output_dir, message_id + ".xml"), "w") as out_file:
        out_file.write(serialized_message)

    tally = Tally(
        creation_time=now,
        collection_date=collection_date,
        total_amount=Decimal(message.cstmr_drct_dbt_initn.grp_hdr.ctrl_sum),  # type: ignore
        contents=serialized_message,
    )
    session.add(tally)
