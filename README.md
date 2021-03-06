# bikeMapping
Creating an application to pull rental bycicle status from a given set of coordinates.

Currently in progress is an API to generate the access token needed to pull results from the LimeBike web API, as my current method relies on my stored personal data, EG packet captures and auth info. Once I can reliably generate a valid access token on the fly, I will be able to add the rest of the library. 

This will eventually result in a pool of data, sampled intermittently, and stored in a database. That database will then be used to plot bike usage and other information against a general map of an area. Eventually, I hope to be able to parse some sense of each individual bike's movement, to generate a weighted map representing usual bike traffic patterns.


Unfortunately, testing has revealed that it is not possible to get live traffic pulls. Obviously this is intentional, as that would allow privacy violations. The best that can be done is interpolation based on locked stationary bikes. Theoretically, this can be used to generate a depth mapping of campus, and show the "hotspots" for bikes to be locked up. Testing with remote unlocking has been successful, replaying a saved packet and spoofing GPS coordinates to be near a designated bike has allowed the bike to be unlocked with merely a plate number. The only other issue is that the plate numbers are not provided within the returned data for local bike scanning. Since active bikes are not shown in the available data, and tags are not given as a result for any query I have access to, there would seem to not be a method for mapping individual bike movement. Given the sheer number of bikes, it is not feasible to coordinate the bike leaving one area and being parked in another either. Further testing is needed to see if there is a method for manipulating the data and getting the desired data.

A current sample of exported data is available here: https://drive.google.com/open?id=1zyGs_iBIcPwYINZXekINIhgKfJW4q13q&usp=sharing
