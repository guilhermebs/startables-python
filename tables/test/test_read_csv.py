from io import StringIO

from ..readers.read_csv import make_table, read_stream_csv
from .. import pdtable
from textwrap import dedent

from ..store import StarBlockType, TableBundle


def test_make_table():
    lines = dedent(r"""
    **input_files_derived;
    all;
    file_bytes;file_date;file_name;has_table;
    -;text;text;onoff;
    15373;20190516T104445;PISA_Library\results\check_Soil_Plastic_ULS1-PISA_C1.csv;1;
    15326;20190516T104445;PISA_Library\results\check_Soil_Plastic_ULS1-PISA_C2.csv;1;
    """).strip().split('\n')
    t = make_table(lines, ';').pdtable
    assert t.file_bytes[0] == 15373

    tt = pdtable.Table(t)
    assert tt.name == 'input_files_derived'
    assert set(tt.metadata.destinations) == {'all'}
    assert tt.units == ['-', 'text', 'text', 'onoff']


def test_parse_onoff():
    lines = dedent(r"""
    **input_files_derived;
    all;
    file_bytes;file_date;has_table;
    -;text;onoff;
    15373;a;0;
    15326;b;1;
    """).strip().split('\n')
    t = make_table(lines, ';').pdtable
    assert t.file_bytes[0] == 15373
    assert t.has_table[0] == False
    assert t.has_table[1] == True
    tt = pdtable.Table(t)
    assert tt.name == 'input_files_derived'
    assert set(tt.metadata.destinations) == {'all'}
    assert tt.units == ['-', 'text', 'onoff']


def test_no_trailing_sep():
    lines=dedent(r"""
    **foo
    all
    column;pct;dash;mm;
    text;%;-;mm;
    bar;10;10;10;
    """).strip().split('\n')
    t = make_table(lines, ';').pdtable
    assert t.column[0] == 'bar'
    assert t.dash[0] == 10


def test_stream():
    lines = dedent(r"""
    **foo
    all
    column;pct;dash;mm;
    text;%;-;mm;
    bar;10;10;10;
    
    ::;Table foo describes
    ;the fooness of things
    :.column;Column is a column in foo
    
    **input_files_derived;
    all;
    file_bytes;file_date;has_table;
    -;text;onoff;
    15373;a;0;
    15326;b;1;
    """)

    with StringIO(lines) as f:
        blocks = [b for b in read_stream_csv(f, sep=';')]
        assert len(blocks) == 8  # includes four blanks and two template rows

    with StringIO(lines) as f:
        table = TableBundle(read_stream_csv(f, sep=';'))

    assert table.foo.column.values[0] == 'bar'
    assert table.foo.dash.values[0] == 10
