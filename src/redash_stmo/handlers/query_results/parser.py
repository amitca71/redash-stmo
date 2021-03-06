#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2018 the sqlparse authors and contributors
# <see AUTHORS file>
#
# This example is part of python-sqlparse and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause
#
# This example illustrates how to extract table names from nested
# SELECT statements.
#
# See:
# https://groups.google.com/forum/#!forum/sqlparse/browse_thread/thread/b0bd9a022e9d4895

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import DML, Keyword


def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == "SELECT":
            return True
    return False


def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword:
                return
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == "FROM":
            from_seen = True


def extract_table_identifiers(token_stream):
    for item in token_stream:
        try:
            if isinstance(item, IdentifierList):
                for identifier in item.get_identifiers():
                    yield identifier.get_real_name()
            elif isinstance(item, Identifier):
                yield item.get_real_name()
            # It's a bug to check for Keyword here, but in the example
            # above some tables names are identified as keywords...
            elif item.ttype is Keyword:
                yield item.value
        except StopIteration:
            return


def extract_table_names(sql):
    stream = extract_from_part(sqlparse.parse(sql)[0])
    return list(extract_table_identifiers(stream))
