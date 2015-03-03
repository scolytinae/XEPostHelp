#-*- coding:utf-8 -*-
#!/usr/bin/python

import re
import argparse
import os

RE_USES = re.compile('(^|\s)uses\s+((.|\n)*)')
RE_IMPLEMENTATION = re.compile('^\s*implementation($|\s)')
RE_INITIALIZATION = re.compile('^\s*initialization($|\s)')
RE_FINALIZATION = re.compile('^\s*finalization($|\s)')
RE_BEGIN = re.compile('(^|\s)(begin|try|case)\s')
RE_END = re.compile('(^|\s)end($|\s|\.)')
RE_FORWARD = re.compile('\s*forward\s*')
RE_PROCEDURE = re.compile('(^|\s)(procedure|function|constructor|destructor)\s+([a-zA-Z\d\.]+).*')

RE_TRACEDEF_START = re.compile('\{AUTO_TRACE_DEFINITION_ST\}')
RE_TRACEDEF_FINISH = re.compile('\{AUTO_TRACE_DEFINITION_FN\}')
RE_TRACECALL_START = re.compile('\{TRACE_CALL_ST\}')
RE_TRACECALL_FINISH = re.compile('\{TRACE_CALL_FN\}')

UNITS_2_ADD = ['RtpConst', 'RtpCtrls']

TRACE_PROCEDURE = '''{AUTO_TRACE_DEFINITION_ST}

{$define AUTO_TRACE}
procedure AutoTracePy(const aMessage: string; const aSender: string);
begin
{$ifdef AUTO_TRACE}
    PostEventMessage(aMessage, ekTrace, aSender);
{$endif} // AUTO_TRACE
end;
{AUTO_TRACE_DEFINITION_FN}'''


TRACE_CALL = """{{TRACE_CALL_ST}}
  AutoTracePy('{0}', '{1}');
{{TRACE_CALL_FN}}"""

def del_trace_function(file_name):
    """Delete trace functions from file"""
    try:
        f = open(file_name, 'r')
        lines = ''.join(f.readlines()).split(';')
    except Exception as e:
        lines = []
    is_trash = False
    str_buf = ''
    new_lines = []
    for l in lines:
        m = RE_TRACEDEF_START.search(l)
        if m:
            is_trash = True
            str_buf = l[:m.start()]

        m = RE_TRACECALL_START.search(l)
        if not is_trash and m:
            is_trash = True
            str_buf = l[:m.start()]
            continue

        if not is_trash:
            new_lines.append(str_buf + l)
            str_buf = ''

        m = RE_TRACEDEF_FINISH.search(l)
        if m:
            is_trash = False
            new_lines.append(str_buf + l[m.end():])
            str_buf = ''

        m = RE_TRACECALL_FINISH.search(l)
        if m:
            is_trash = False
            str_buf = str_buf + l[m.end():]
            if str_buf:
                new_lines.append(str_buf)
            str_buf = ''

    with open(file_name, 'w') as f:
        f.write(';'.join(new_lines))


def add_trace_function(file_name):
    """Add trace function in each procedure/function"""
    trace_sender = os.path.basename(file_name)
    try:
        f = open(file_name, 'r')
        lines = ''.join(f.readlines()).split(';')
    except Exception as e:
        lines = []

    new_lines = []
    begin_depth = 0
    procedure_stack = []
    block_flag = (False, False, False)
    is_first_procedure = True
    is_uses_added = False

    for l in lines:
        if block_flag[1] and RE_FINALIZATION.match(l):
            new_lines.append(TRACE_CALL.format('Finish initialization', trace_sender))

        m = RE_END.search(l)
        if m:
            if block_flag[1] and (m.group(2) == '.'):
                new_lines.append(TRACE_CALL.format('Finish initialization', trace_sender))
            elif block_flag[2] and (m.group(2) == '.'):
                new_lines.append(TRACE_CALL.format('Finish finalization', trace_sender))
            elif block_flag[0] and (m.group(2) != '.'):
                try:
                    proc_info = procedure_stack[-1]
                    if proc_info[0] == begin_depth:
                        new_lines.append(TRACE_CALL.format('Finish ' + proc_info[1], trace_sender))
                        procedure_stack.pop()
                except Exception as e:
                    print('No proc_info', e)
                finally:
                    begin_depth -= 1

        m = RE_USES.search(l)
        if m:
            uses_list = m.group(2).split(',')
            striped_list = [x.strip() for x in uses_list]
            for unit in UNITS_2_ADD:
                if is_uses_added and unit in striped_list:
                    uses_list.pop(striped_list.index(unit))
                    striped_list.remove(unit)
                if not (is_uses_added or unit in striped_list):
                    uses_list.append(unit)
            is_uses_added = True
            l = l[:m.start(2)] + ','.join(uses_list)

        new_lines.append(l)

        if block_flag[0] and RE_FORWARD.search(l):
            procedure_stack.pop()

        m = RE_BEGIN.search(l)
        if block_flag[0] and m:
            try:
                proc_info = procedure_stack[-1]
                if (proc_info[0] - 1) == begin_depth:
                    new_lines.pop()
                    insert_line = l[:m.end()] + TRACE_CALL.format('Begin ' + proc_info[1], trace_sender) + l[m.end():]
                    new_lines.append(insert_line)
            except:
                pass
            finally:
                begin_depth += len(RE_BEGIN.findall(l))

        m = RE_PROCEDURE.search(l)
        if block_flag[0] and m:
            if is_first_procedure:
                buf = TRACE_PROCEDURE + new_lines.pop()
                new_lines.append(buf)
                is_first_procedure = False
            procedure_stack.append((begin_depth + 1, m.group(3)))

        if RE_IMPLEMENTATION.match(l):
            block_flag = (True, False, False)

        m = RE_INITIALIZATION.match(l)
        if m:
            block_flag = (False, True, False)
            new_lines.pop()
            insert_line = l[:m.end()] + TRACE_CALL.format('Begin initialization', trace_sender) + l[m.end():]
            new_lines.append(insert_line)

        m = RE_FINALIZATION.match(l)
        if m:
            block_flag = (False, False, True)
            new_lines.pop()
            insert_line = l[:m.end()] + TRACE_CALL.format('Begin finalization', trace_sender) + l[m.end():]
            new_lines.append(insert_line)

    with open(file_name + '', 'w') as f:
        f.write(';'.join(new_lines))


def _get_arguments():
    """Read command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='*.pas file')
    parser.add_argument('-c', '--clear', action='store_true', help='remove trace function')
    return parser.parse_args()


if __name__ == "__main__":
    args = _get_arguments()
    if args.clear:
        del_trace_function(args.file)
    else:
        add_trace_function(args.file)