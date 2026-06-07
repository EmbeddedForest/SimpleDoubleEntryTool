#------------------------------------------------------------------------------
# File:
#   core/config.py
#
# Description:
#   Loads config.yaml. Kept tiny and separate so both the importer and the
#   accounts model can share one definition of "how config is read".
#------------------------------------------------------------------------------

import yaml

import constants as c


class ConfigNotFoundError(FileNotFoundError):
    ''' Raised when the config file is missing. '''


def load_config(path=c.CONFIG_FILE):
    try:
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        raise ConfigNotFoundError(path) from e
