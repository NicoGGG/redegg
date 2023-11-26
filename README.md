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
- [ ] Make a command to scrape only a list of fighters. This will be used to update only the fighters that are in a specific event
- [ ] Make the model, view and template for contest leaderboard
- [ ] Make the model, view and template for global leaderboard
- [ ] Implement social auth for twitter and reddit
- [ ] Make the view and template for user settings (?)
