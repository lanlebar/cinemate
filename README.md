# Cinemate
Web-based application - search for movies and TV shows and add them to your liked list. With user auth and database for user managment. \
Can also generate 'random' movies - I'm feeling lucky functionality. \
When user finds the movie, he can like it - added to liked list. User can then search for movies in that list or sort liked movies (by IMDB rating, title or year) \
\
I made Cinemate for a final project for my programming in class. I didn't really have any intension of publishing it, its more like a dummy project

## Tech used
- **Python Flask** -  I'm really comfortable in Python so I didn't think twice before choosing my backend language. I also used libraires like Levenshtein and hashlib to complete my application
- **TinyDB** - used for user managment. Tbh, I was too lazy to integrate a real RDBMS to this dummy project :)
- **Ajax** - asynchronous stuff
- **HTML, CSS, JS**: nothing special for the front-end. UI/UX wasn't really my priority with this project, this explains the not so preety visuals of it :)
- **APIs and other tools**
  - OMDB API - to get movie information from users search queriers
  - TMDB API - used to enable the 'I'm feeling lucky' - gets a random movie
