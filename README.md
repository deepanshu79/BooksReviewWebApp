# SeeBooks

This project implements a books reviewing web application using flask (python framework) , postgreSQL , SQLAlchemy , Jinja2 , goodreads API and python.

Database URL = `postgres://jifsoieydfzqwo:d75adba98c2741a006e5ef607225079ce462717d761b2a58fe469d4ec64dc790@ec2-52-7-39-178.compute-1.amazonaws.com:5432/d2d2rpvo1o7du6`

Features available on website :

Register - First of all user need to register to website with a username , password and email address . Registering with an username already taken or with incomplete details will result in a error message.

Login - Registered user will then be able to login in to the website . An login attempt with valid username and password will take the user to profile dashboard otherwise the login attempt will result in a error message.

Search - Logged in user will then be able to search for books by their ISBN no. , title , author name . The result of this search will be list of books having matching details . If there was no such book in database then a message will be displayed for same.

Review statistics - Clicking on one of the search results will take the user to a page having review statistics about that book fetched using goodreads API. This page will also show the available reviews about that book(if any).

Submitting review - On the book details page , user will also be able to submit his/her own review consisting of rating and text review . After review submission the page will update/refresh itself to show the user review . In case of second review submission by user on the same book , an error message will be displayed.

Dashboard/logout - Logged in user will be able to go back to their profile page by using dashboard link and similarly will be able to logout from the website using logout link.

Json response - User will be able to get an Json response having details about the book by using - Default route/api/isbn - where Default route is the URL(the hosting address) of website and isbn is the ISBN number of the book for which the json response is to be fetched.

Files :

application.py - Implements the whole website using routes.

import.py - Imports the books details from the books.csv file into the database.

templates - Include all the html pages.

requirements.txt - Mentions requirements for running website on browser.
