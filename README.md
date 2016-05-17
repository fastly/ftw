## Framework for Testing WAFs (FTW)

##### Purpose 
This project was created by researchers from ModSecurity and Fastly to help provide rigorous tests for WAF rules. It uses the OWASP Core Ruleset V3 as a baseline to test rules on a WAF. Each rule from the ruleset is loaded into a YAML file that issues HTTP requests that will trigger these rules. 

Goals / Use cases include:

* Find regressions in WAF deployments by using continuous integration and issuing repeatable attacks to a WAF
* Provide a testing framework for new rules into ModSecurity, if a rule is submitted it MUST have corresponding positive & negative tests
* Evaluate WAFs against a common, agreeable baseline ruleset (OWASP)
* Test and verify custom rules for WAFs that are not part of the core rule set

## Installation
* `git clone git@github.com:fastly/ftw.git`
* `cd ftw`
* `pip install -r requirements.txt`

## Running Tests
* *start your test web server*
* Create YAML files that point to your webserver with a WAF in front of it
* `py.test test/test_modsecurityv2.py --ruledir test/yaml`

## Running Tests while overriding destination address in the yaml files to custom domain
* *start your test web server*
* `py.test test/test_modsecurityv2.py --ruledir=test/yaml --destaddr=domain.com`
