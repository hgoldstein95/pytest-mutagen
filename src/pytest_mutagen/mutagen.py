from os import path


APPLY_TO_ALL = "**all**"

# Global list of all mutants
g_mutant_registry = {APPLY_TO_ALL:{}}

# Current mutant (set by Mutant::apply_and_run)
g_current_mutant = None

class Mutant(object):
    def __init__(self, name, description):
        self.function_mappings = {}
        self.name = name
        self.description = description

    def add_mapping(self, fname, fimpl):
        self.function_mappings[fname] = fimpl

    def apply_and_run(self, f):
        global g_current_mutant
        g_current_mutant = self
        result = True
        try:
            f()
        except Exception:
            result = False
        g_current_mutant = None

        return result


def active_mutant(mutation):
    global g_current_mutant
    return g_current_mutant and \
        g_current_mutant.name == mutation


def not_mutant(mutation):
    return not active_mutant(mutation)


def mut(mutation, good, bad):
    global g_current_mutant

    if g_current_mutant and g_current_mutant.name == mutation:
        return bad()
    else:
        return good()


def mutant_of(fname, mutant_name, file=None, description=""):

    def decorator(f):
        basename = file if not file is None else path.basename(f.__globals__['__file__'])
        has_mutant(mutant_name, basename, "")(f)

        if isinstance(basename, str):
            g_mutant_registry[basename][mutant_name].add_mapping(fname, f)
        else:
            for b in basename:
                g_mutant_registry[b][mutant_name].add_mapping(fname, f)

        return f

    return decorator

def has_mutant(mutant_name, file=None, description=""):

    def decorator(f):
        if file is None:
            files = [APPLY_TO_ALL]
        elif isinstance(file, str):
            files = [file]
        elif isinstance(file, list):
            files = file
        else:
            raise ValueError("file must be a string or a list of strings")

        for basename in files:
            if basename not in g_mutant_registry:
                g_mutant_registry[basename]=  {}

            if mutant_name not in g_mutant_registry[basename]:
                g_mutant_registry[basename][mutant_name] = Mutant(mutant_name, description)
        return f

    return decorator