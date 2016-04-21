### OWASP-CRS-Regressions

##### What is this repo?
These are the unit tests for crs-regressions.
Before any new rule is accepted it must have unit tests prepared for it.
The unit tests are written in YAML. Unlike the rules for the ModSecurity Core, these rules do not require you to include the physical rule.

#PreRequistes.
* YAML Parsing.
    * YAML parsing does not come preequipped with python (yet). As a result, we use PyYAML. Any YAML parser should work equally well, but this configuration is tested using PyYAML version 3.11
