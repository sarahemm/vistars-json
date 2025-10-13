# Vistars-JSON

Outputs LHC vistars data as JSON, used in lhcstatus2 social media

Status data is read from CERN's vistar pages:
  - (Page1)[https://op-webtools.web.cern.ch/vistar/?usr=LHC1]
  - (Configuration)[https://op-webtools.web.cern.ch/vistar/?usr=LHCCONFIG]
  - (Operation)[https://op-webtools.web.cern.ch/vistar/?usr=LHC3]
  - (Cryogenics)[https://op-webtools.web.cern.ch/vistar/?usr=LHC2]

The unit property (in schema) follows (https://dataprotocols.org/units/)[https://web.archive.org/web/20221224145746/https://dataprotocols.org/units/]

experiment->operation: **Floating point data may contain NaN**. This could break certain JSON parsers.

experiment->config: Given as strings, not numbers/integers, may contain things like "no_value(V)", "-".
Luminosity dimensions are skipped.

cryo->state: An array containing one array for each colour bar on the lhc2 page. Each element represents a cryomodule/cryostat.
Possible values 0, 1, 2, 3; 0 = green, 1 = red, 2 = orange, 3 = blue
Orange indicates a state between red and green, for example one which is close to recovering.
Blue ? (only seen for CMS so far).
FYI: The CMS solenoid and ATLAS toroid & solenoid may lose cryogenic conditions without affecting the beam.
