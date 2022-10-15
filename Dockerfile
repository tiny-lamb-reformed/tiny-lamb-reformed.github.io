FROM ruby:2.7.4-slim

RUN apt-get update \
  && apt-get install -y build-essential

WORKDIR /home
COPY docs/Gemfile .

RUN bundle install

CMD [ "bundle", "exec", "jekyll", "serve", "--host=0.0.0.0" ]
EXPOSE 4000
