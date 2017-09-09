# A database of irregular (and regular) Spanish verbs

This database is based on [Fred Jehle's Conjugated Spanish Verb Database](https://github.com/ghidinelli/fred-jehle-spanish-verbs).

There are several problems with the original database:

* the format it uses is very redundant, so adding new verbs is a chore
* there are no English translations corresponding to 1/2/3 person plural/singular
* there are some errors in the database, such as a mixed up order of imperative forms, missing 1st person plural imperative forms, or missing 1st and 2nd person forms for some verbs

The conversion scripts are saved in the `jehle_conversion` folder, look into the `corrections` files for more details about the things that were fixed.

This repo contains the database cleaned from redundancies (only irregular forms are listed), and an accompanying template for generating the remaining regular forms.
In addition, there are English translation templates for the verbs, which makes it more convenient for generating flashcards.
