# intesisHome for Docker

This image uses the IntesisHome python library from https://github.com/jnimmo/pyIntesisHome
It will start a web-server on port 8000 and listen to requests in the form
of:
> http://[dockerhost]:[containerport]/cmd?[command]

Where command is any of the following:

* on - Power on
* off - Power off
* heat - Set mode to 'heat'
* cool - Set mode to 'cool'
* dry - Set mode to 'dry'
* auto - Set mode to 'auto'
* fan_quiet - Set fan speed to 'quiet'
* fan_low - Set fan speed to 'low'
* fan_medium - Set fan speed to 'medium'
* fan_high - Set fan speed to 'high'
* fan_auto - Set fan speed to 'auto'
* 10-39 - Set temperature to X

# Building the image
Is as simple as:
> ./build.sh

# Running the container
> docker run -it -e INTESIS_USER=myself -e INTESIS_PASS=sosecret intesishome