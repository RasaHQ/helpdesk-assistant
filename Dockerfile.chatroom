# docker build -t chatroom -f Dockerfile.chatroom
# docker run --name chatroom -p 8080:3000 -d chatroom
FROM node:14

RUN node --version

RUN git clone https://github.com/RasaHQ/chatroom.git

WORKDIR /chatroom

RUN curl -o- -L https://yarnpkg.com/install.sh | bash
RUN yarn

# replace default chatroom index.html
COPY chatroom_handoff.html index.html

RUN yarn build

EXPOSE 8080

CMD [ "yarn", "serve" ]