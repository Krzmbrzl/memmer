# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.


def container_unordered_equals(lhs, rhs, eq_cmp=None) -> bool:
    if len(lhs) != len(rhs):
        return False

    def default_cmp(l, r):
        return l == r

    if eq_cmp is None:
        eq_cmp = default_cmp

    matched_indices = set()

    for lhs_elem in lhs:
        found = False
        for i, rhs_elem in enumerate(rhs):
            if i in matched_indices:
                # Matching the same index multiple times can happen in case of duplicates
                continue
            if not eq_cmp(lhs_elem, rhs_elem):
                continue

            matched_indices.add(i)
            found = True
            break

        if not found:
            return False

    return True
