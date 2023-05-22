def list_all_lang():
    from os.path import dirname, basename, isfile
    import glob
    # This generates a list of lang in this folder for the * in __main__ to work.
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    all_lang = [basename(f)[:-3] for f in mod_paths if isfile(f)
                   and f.endswith(".py")
                   and not f.endswith('__init__.py')]

    return all_lang
