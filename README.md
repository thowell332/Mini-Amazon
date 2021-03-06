# Welcome to Mini Amazon!

This website is a data driven web application that relies on Flask and PostgreSQL to emulate the functionality of an online marketplace like Amazon. To run the website, go into the repository directory and issue the following commands:
```
source env/bin/activate
flask run
```
The first command will activate a specialized Python environment for running Flask.
While the environment is activated, you should see a `(env)` prefix in the command prompt.
You should only run Flask while inside this environment; otherwise it might produce an error.

To stop your website, simply press <kbd>Ctrl</kbd><kbd>C</kbd> in the shell where flask is running.
You can then deactivate the environment using
```
deactiviate
```

## Database E/R Diagram

The E/R diagram for the Mini Amazon database is shown below.

![cs316_final_er drawio](https://user-images.githubusercontent.com/65472983/147299702-108c965e-c6ee-4115-bfbe-1bdfb2b82bf3.png)
