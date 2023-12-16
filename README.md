# Redegg project

![workflow build](https://github.com/NicoGGG/redegg/actions/workflows/build.yml/badge.svg)

Source code for the Redegg application.

## TODO

- [x] Make the view and template for contest listing
- [x] Display points and bonus on the view_prediction template
- [x] Add a method is_draw in the Fight model for easier condition checking of the fight result.
- [x] Make the view and template for prediction listing and prediction detail
- [x] Make the application and celery work with docker and docker compose
  - [x] web and celery services should have the same Dockerfile of the entire django project
  - [x] Docker compose with 5 containers: web, db, celery, rabbitmq, and nginx
  - [x] Django settings customization for: db type and host, celery broker and backend, static files, media files
  - [x] Scraper (celery worker) should always use the same database as the web application and replace all the api call with Object calls. The signals now work for some reason so no need to use the api
- [x] Deploy on my VPS
- [x] Make the model, view and template for contest leaderboard
- [x] Make the model, view and template for global leaderboard
- [x] Implement social auth for twitter and reddit
  - [x] Twitter
  - [x] Reddit
  - [x] Templates
- [x] Add bonus points for consecutive correct predictions
- [x] Add a discord notification when a Fight is deleted
- [x] Display the rules and point counting somewhere
- [x] Make a command to scrape only a list of fighters. This will be used to update only the fighters that are in a specific event
- [x] Disable allauth unused urls
  - [x] Write a quick article on how to do it
- [x] Easier access to the leaderboard of a specific contest
- [x] Branding
  - [x] Buy the domain name
  - [x] Make a logo and favicon
- [x] Add notification when a user is created / Disable user username (or at least make it not unique)
- [ ] Make the html for base and at least create_prediction nice to view on phone
  - [x] Minimal usable on phone
  - [ ] Full usable on phone and nice to view
- [x] Add Fighter nationality and display flag on the prediction pages (view, create, and detail)
- [ ] Add possibility to prognostic the finish round of the fight
- [ ] Refactor the html templates to limit code duplication, especially on the fight-result div
- [ ] Implement rate limits, especially on the admin page: [Django Rate Limit](https://django-ratelimit.readthedocs.io/en/stable/installation.html) and a [snipet](https://gist.github.com/nitely/5202285). Else, maybe use [Traefik rate limit](https://doc.traefik.io/traefik/middlewares/http/ratelimit/)
- [ ] Monthly leaderboard
- [ ] Leaderboard by community (reddit, twitter, etc.)
- [ ] Private leaderboard
- [ ] Make the view and template for user settings (?)
