#._cv_part guppy.gsl.Exceptions

class DebugError(Exception):
    # An error raised for debugging
    # when we want to look at the error at the place it really happened
    # rather than catch it, try to go on for more messages
    pass

class GSL_Error(Exception):
    pass

class TooManyErrors(GSL_Error):
    pass

class HadReportedError(GSL_Error):
    pass

class ReportedError(GSL_Error):
    pass

class UndefinedError(ReportedError):
    pass

class DuplicateError(ReportedError):
    pass

class CompositionError(GSL_Error):
    pass

class CoverageError(ReportedError):
    pass

class ConditionError(GSL_Error):
    pass

