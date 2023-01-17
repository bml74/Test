# Usage

### To run:

1. Activate virtual environment

```pipenv shell```

2. Test virtual environment was created

```pip list```

See if a bunch of packages show up. If yes, then pipenv was created!

3. To run dev server:

```python3 manage.py runserver```



### To add to GitHub and Heroku:

1. ``` git add . ``` (Add)
2. ``` git commit -m "DESCRIPTION" ``` (Commit)
3. ``` git push -f origin main ``` (Push to GitHub)
4. ``` git push heroku main ``` (Push to Heroku)


### To run PyTest

1. Navigate to home directly
2. Select test you want to do. In this example, we will run the userCreatedSuccessfully test in the UserTestCase class in the tests.py file in the users app.
3. Run command. In this case: 
```
./manage.py test users.tests.UserTestCase.userCreatedSuccessfully
```


