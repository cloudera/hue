import csv
import cffi

# IN-PROGRESS.  See the demo at the end of the file


def _make_ffi_from_dialect(dialect_name):
    dialect = csv.get_dialect(dialect_name)

    ffi = cffi.FFI()

    ffi.cdef("""
        long parse_line(char *rawline, long inputlength);
    """)

    d = {'quotechar': ord(dialect.quotechar),
         'quoting': int(dialect.quoting),
         'skipinitialspace': int(dialect.skipinitialspace),
         'delimiter': ord(dialect.delimiter),
         'doublequote': int(dialect.doublequote),
         'strict': int(dialect.strict),
         }
    if dialect.escapechar is not None:
        d['is_escape_char'] = '== %d' % ord(dialect.escapechar)
    else:
        d['is_escape_char'] = '&& 0'

    ffi.set_source('_fastcsv_' + dialect_name, r'''

    typedef enum {
        START_RECORD, START_FIELD, ESCAPED_CHAR, IN_FIELD,
        IN_QUOTED_FIELD, ESCAPE_IN_QUOTED_FIELD, QUOTE_IN_QUOTED_FIELD,
        EAT_CRNL
    } ParserState;

    typedef enum {
        QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE
    } QuoteStyle;

    typedef struct {
        ParserState state;          /* current CSV parse state */
        char *field;                /* build current field in here */
        int field_size;             /* size of allocated buffer */
        int field_len;              /* length of current field */
        int numeric_field;          /* treat field as numeric */
    } ReaderObj;

    static void
    parse_add_char(ReaderObj *self, char c)
    {
        *self->field++ = c;
    }

    static void
    parse_save_field(ReaderObj *self)
    {
        *self->field++ = 0;
    }

    static int
    parse_process_char(ReaderObj *self, char c)
    {
        switch (self->state) {
        case START_RECORD:
            /* start of record */
            if (c == '\0')
                /* empty line - return [] */
                break;
            else if (c == '\n' || c == '\r') {
                self->state = EAT_CRNL;
                break;
            }
            /* normal character - handle as START_FIELD */
            self->state = START_FIELD;
            /* fallthru */
        case START_FIELD:
            /* expecting field */
            if (c == '\n' || c == '\r' || c == '\0') {
                /* save empty field - return [fields] */
                parse_save_field(self);
                self->state = (c == '\0' ? START_RECORD : EAT_CRNL);
            }
            else if (c == %(quotechar)d &&
                     %(quoting)d != QUOTE_NONE) {
                /* start quoted field */
                self->state = IN_QUOTED_FIELD;
            }
            else if (c %(is_escape_char)s) {
                /* possible escaped character */
                self->state = ESCAPED_CHAR;
            }
            else if (c == ' ' && %(skipinitialspace)d)
                /* ignore space at start of field */
                ;
            else if (c == %(delimiter)d) {
                /* save empty field */
                parse_save_field(self);
            }
            else {
                /* begin new unquoted field */
                if (%(quoting)d == QUOTE_NONNUMERIC)
                    self->numeric_field = 1;
                parse_add_char(self, c);
                self->state = IN_FIELD;
            }
            break;

        case ESCAPED_CHAR:
            if (c == '\0')
                c = '\n';
            parse_add_char(self, c);
            self->state = IN_FIELD;
            break;

        case IN_FIELD:
            /* in unquoted field */
            if (c == '\n' || c == '\r' || c == '\0') {
                /* end of line - return [fields] */
                parse_save_field(self);
                self->state = (c == '\0' ? START_RECORD : EAT_CRNL);
            }
            else if (c %(is_escape_char)s) {
                /* possible escaped character */
                self->state = ESCAPED_CHAR;
            }
            else if (c == %(delimiter)d) {
                /* save field - wait for new field */
                parse_save_field(self);
                self->state = START_FIELD;
            }
            else {
                /* normal character - save in field */
                parse_add_char(self, c);
            }
            break;

        case IN_QUOTED_FIELD:
            /* in quoted field */
            if (c == '\0')
                ;
            else if (c %(is_escape_char)s) {
                /* Possible escape character */
                self->state = ESCAPE_IN_QUOTED_FIELD;
            }
            else if (c == %(quotechar)d &&
                     %(quoting)d != QUOTE_NONE) {
                if (%(doublequote)d) {
                    /* doublequote; " represented by "" */
                    self->state = QUOTE_IN_QUOTED_FIELD;
                }
                else {
                    /* end of quote part of field */
                    self->state = IN_FIELD;
                }
            }
            else {
                /* normal character - save in field */
                parse_add_char(self, c);
            }
            break;

        case ESCAPE_IN_QUOTED_FIELD:
            if (c == '\0')
                c = '\n';
            parse_add_char(self, c);
            self->state = IN_QUOTED_FIELD;
            break;

        case QUOTE_IN_QUOTED_FIELD:
            /* doublequote - seen a quote in an quoted field */
            if (%(quoting)d != QUOTE_NONE &&
                c == %(quotechar)d) {
                /* save "" as " */
                parse_add_char(self, c);
                self->state = IN_QUOTED_FIELD;
            }
            else if (c == %(delimiter)d) {
                /* save field - wait for new field */
                parse_save_field(self);
                self->state = START_FIELD;
            }
            else if (c == '\n' || c == '\r' || c == '\0') {
                /* end of line - return [fields] */
                parse_save_field(self);
                self->state = (c == '\0' ? START_RECORD : EAT_CRNL);
            }
            else if (!%(strict)d) {
                parse_add_char(self, c);
                self->state = IN_FIELD;
            }
            else {
                /* illegal */
                /*PyErr_Format(error_obj, "'%%c' expected after '%%c'",
                                dialect->delimiter,
                                dialect->quotechar);*/
                return -1;
            }
            break;

        case EAT_CRNL:
            if (c == '\n' || c == '\r')
                ;
            else if (c == '\0')
                self->state = START_RECORD;
            else {
                /*PyErr_Format(error_obj, "new-line character seen in unquoted field - do you need to open the file in universal-newline mode?");*/
                return -1;
            }
            break;

        }
        return 0;
    }

    static void
    parse_reset(ReaderObj *self, char *rawline)
    {
        self->field = rawline;
        self->state = START_RECORD;
        self->numeric_field = 0;
    }

    long parse_line(char *rawline, long inputlength)
    {
        char *p;
        ReaderObj reader;
        parse_reset(&reader, rawline);

        for (p=rawline; inputlength > 0; inputlength--, p++) {
            if (parse_process_char(&reader, *p) < 0)
                return -1;
        }
        if (parse_process_char(&reader, 0) < 0)
            return -1;
        return reader.field - rawline - 1;
    }
    ''' % d)

    ffi.compile()


def fastcsv_reader(f, dialect_name):
    try:
        module = __import__('_fastcsv_' + dialect_name)
    except ImportError:
        _make_ffi_from_dialect(dialect_name)
        module = __import__('_fastcsv_' + dialect_name)
    ffi, lib = module.ffi, module.lib
    #
    linelen = -1
    for line in f:
        if linelen <= len(line):
            linelen = 2 * len(line)
            rawline = ffi.new("char[]", linelen)
        ffi.buffer(rawline, len(line))[:] = line
        n = lib.parse_line(rawline, len(line))
        assert n >= 0
        yield ffi.buffer(rawline, n)[:].split('\x00')


if __name__ == '__main__':
    csv.register_dialect('unixpwd', delimiter=':', quoting=csv.QUOTE_NONE)
    with open('/etc/passwd', 'rb') as f:
        reader = fastcsv_reader(f, 'unixpwd')
        for row in reader:
            print row
