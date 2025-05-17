# Sweeter

Sweeter is a web application built using Flask and MongoDB. It allows users to sign up, log in, create posts, and interact with other users' posts through likes. This project is part of the MSIB LearningX Full Stack Web Development Basic program.

## Features

- **User Authentication**: Users can sign up, log in, and manage their profiles.
- **Posting**: Users can create posts with comments and dates.
- **Likes**: Users can like posts with different reactions (heart, star, thumbs up).
- **Profile Management**: Users can update their profile information and profile pictures.
- **Dynamic Pages**: Pages like home, login, user profile, about, and secret are dynamically rendered.

## Project Structure

```
app.py
requirements.txt
start.sh
static/
    favico.ico
    logo.png
    myjs.js
    mystyle.css
    ogimage.jpg
    profile_pics/
        profile_placeholder.png
        test.jpeg
templates/
    about.html
    index.html
    login.html
    secret.html
    user.html
```

- **app.py**: The main application file containing all the routes and logic.
- **requirements.txt**: Contains the Python dependencies for the project.
- **start.sh**: A shell script to start the application.
- **static/**: Contains static files like images, JavaScript, and CSS.
- **templates/**: Contains HTML templates for rendering pages.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd sweeter
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory

4. Start the application:

   ```bash
   python app.py
   ```

5. Access the application at `http://localhost:5000`.

## Usage

- **Sign Up**: Create a new account.
- **Log In**: Log in with your credentials.
- **Create Posts**: Add new posts with comments and dates.
- **Like Posts**: Interact with posts using different reactions.
- **Update Profile**: Edit your profile information and upload a profile picture.

## License

This project is part of the MSIB LearningX Full Stack Web Development Basic program and is intended for educational purposes.
