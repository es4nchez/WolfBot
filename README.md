<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wolf Bot</title>
</head>
<body>

<h1>Wolf Bot</h1>

<p>Welcome to Wolf Bot! This bot provides various functionalities for Discord servers. Follow the steps below to get the bot up and running on your server.</p>

<h2>Setup</h2>

<ol>
    <li><strong>Register a new application/bot on <a href="https://discord.com/developers/applications">Discord Developer Portal</a>:</strong>
        <ul>
            <li>Go to the Discord Developer Portal and create a new application.</li>
            <li>Navigate to the "Bot" section and add a new bot to your application.</li>
            <li>Copy the bot token provided by Discord.</li>
        </ul>
    </li>
    <li><strong>Invite the bot to your server:</strong>
        <ul>
            <li>Generate an invite link for your bot from the "OAuth2" section of your application dashboard.</li>
            <li>Select the required permissions for your bot (e.g., send messages, read message history) and generate the invite link.</li>
            <li>Paste the invite link into your browser and invite the bot to your server.</li>
        </ul>
    </li>
    <li><strong>Configure bot credentials:</strong>
        <ul>
            <li>Rename <code>secrets.yml.example</code> in the <code>config/</code> directory to <code>secrets.yml</code>.</li>
            <li>Open <code>secrets.yml</code> and fill in the bot token and any other necessary IDs or credentials.</li>
        </ul>
    </li>
</ol>

<h2>Running the Bot</h2>

<p>After setting up your bot and configuring credentials, follow these steps to build and run the bot using Docker:</p>

<pre>
docker build -t wolf-bot .
docker run -d --name my-wolf-bot -p 8001:8001 wolf-bot
</pre>

<p>This will build the Docker image and run the bot container, exposing port 8001 for communication.</p>

</body>
</html>
