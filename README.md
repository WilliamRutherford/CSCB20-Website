# CSCB20 Website
 A dynamic website written using HTML/CSS/JS, with a backend in Flask, using a SQLlite database

Frontend code contributed by Oceana Ling-Kurie

## Features

Multiple user accounts of varying types, each with access to unique features.

Website dynamically adjusts to different content, using pre-defined templates to avoid code reuse. 

Accounts stored securely using hashed+salted passwords encoded in base64. Fields are escaped to disallow SQL injection. 

  MD5 was used even though it is highly unsafe, because this was a fake website. 

Database Schema planned out in advance, clearly defined above the relevant functions/routes. 


