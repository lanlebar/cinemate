# Cinemate
Cinemate is a web-based application that allows users to search for movies and TV shows and add them to their liked list. Users can also explore movies with the "I'm feeling lucky" functionality. App requires user to make an account in order to use the app - user auth and database managment in the background. \
\
I created Cinemate as part of my programming class's final project. It was primarily designed as a dummy project and wasn't intended for publication or real-world use.

## Features
- Movies and TV shows search - the search functionality utilizes the OMDB API to retrieve movie information based on user queries.
- I'm feeling lucky - generate random movies and TV shows using the TMDB API.
- Liked list - users can add movies and TV shows to their liked list. Users can then search the list (using Levenshtein for fuzzy searching) or sort their liked movies by IMDB rating, title or year
- User auth - each user has to be register in order to use the app - TinyDB used for database functionality. When registered, user gets its own table, where liked movies are stored

## Tech stack
- **Python Flask**
- **TinyDB** - was to lazy to impliment actual RDBMS
- **Ajax**
- **HTML, CSS, JS** - nothing special for the front-end. UI/UX wasn't really my priority with this project, this explains the not so preety visuals of it
- **APIs and other tools**
  - OMDB API - to get movie information from users search queriers
  - TMDB API - used to enable the 'I'm feeling lucky' - gets a random movie

## Installation
- git clone *https://github.com/lanlebar/cinemate.git*
- cd cinemate
- python main.py (run the main.py file)
- app is running on 127.0.0.1:8080 (usually)
