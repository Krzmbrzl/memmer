# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Tuple, List

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal

from memmer.generated.pain import *
from memmer.generated.pain import __NAMESPACE__
from memmer.orm import Member, Setting
from memmer.queries import compute_total_fee

from sqlalchemy.orm import Session
from sqlalchemy import select

from xsdata.models.datatype import XmlDateTime, XmlDate
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


@dataclass
class CreditorInfo:
    name: str
    iban: str
    bic: str
    identification: str


def create_sepa_transactions(
    session: Session,
    end_to_end_id: str,
    purpose: str,
) -> Tuple[Decimal, List[DirectDebitTransactionInformation9]]:
    members = session.scalars(
        select(Member).where(Member.sepa_mandate_date != None).order_by(Member.id.asc())
    ).all()

    transactions = []
    total = Decimal(0)

    for current_member in members:
        fee = compute_total_fee(session=session, member=current_member)
        total += fee

        if fee > 0:
            e2e_id = end_to_end_id.format(mem_id=current_member.id)

            mandate_signed = current_member.sepa_mandate_date
            assert mandate_signed != None

            transactions.append(
                DirectDebitTransactionInformation9(
                    pmt_id=PaymentIdentification1(end_to_end_id=e2e_id),
                    instd_amt=ActiveOrHistoricCurrencyAndAmount(
                        ccy="EUR", value="{:.2f}".format(fee) # type: ignore
                    ),
                    drct_dbt_tx=DirectDebitTransaction6(
                        mndt_rltd_inf=MandateRelatedInformation6(
                            # We reuse the member ID as the SEPA mandate ID
                            mndt_id=str(current_member.id),
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
                            othr=GenericFinancialIdentification1(id="NOTROVIDED")
                        )
                    ),
                    dbtr=PartyIdentification32(nm=current_member.last_name),
                    dbtr_acct=CashAccount16(
                        id=AccountIdentification4Choice(iban=current_member.iban)
                    ),
                    ultmt_dbtr=PartyIdentification32(
                        nm="{}, {}".format(
                            current_member.last_name, current_member.first_name
                        )
                    ),
                    rmt_inf=RemittanceInformation5(ustrd=[purpose]),
                )
            )

    return (total, transactions)


def create_sepa_payment_initiation_message(
    session: Session, msg_id: str, creditor_info: CreditorInfo, collection_date: date
) -> str:
    now = datetime.now()

    e2e_id_template = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_E2E_ID_TEMPLATE)
    ).one()
    purpose = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_PURPOSE)
    ).one()

    total_sum, transactions = create_sepa_transactions(
        session, e2e_id_template, purpose
    )

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
        ctrl_sum="{:.2f}".format(total_sum), # type: ignore
        initg_pty=PartyIdentification32(nm=creditor_info.name),
    )

    payment_type = PaymentTypeInformation20(
        svc_lvl=ServiceLevel8Choice(cd="SEPA"),
        lcl_instrm=LocalInstrument2Choice(cd="CORE"),
        seq_tp=SequenceType1Code.RCUR,
    )
    creditor = PartyIdentification32(nm=creditor_info.name)
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
        ctrl_sum="{:.2f}".format(total_sum), # type: ignore
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

    doc = Document(cstmr_drct_dbt_initn=init)

    namespace = __NAMESPACE__
    config = SerializerConfig(
        pretty_print=True, schema_location=namespace + " pain.008.001.02.xsd"
    )
    serializer = XmlSerializer(config=config)
    return serializer.render(doc, ns_map={None: namespace})
