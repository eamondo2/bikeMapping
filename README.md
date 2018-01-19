# bikeMapping
Creating an application to pull rental bycicle status from a given set of coordinates.

Currently in progress is an API to generate the access token needed to pull results from the LimeBike web API, as my current method relies on my stored personal data, EG packet captures and auth info. Once I can reliably generate a valid access token on the fly, I will be able to add the rest of the library. 

This will eventually result in a pool of data, sampled intermittently, and stored in a database. That database will then be used to plot bike usage and other information against a general map of an area. Eventually, I hope to be able to parse some sense of each individual bike's movement, to generate a weighted map representing usual bike traffic patterns.
