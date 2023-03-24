# Team NewHappy Large Group project

Personal Spending Tracker - NewHappy

## Team members
The members of the team are:
- Jiale Yang (jiale.2.yang@kcl.ac.uk)
- Runxin Shao (runxin.shao@kcl.ac.uk)
- Zhihao Wu (zhihao.wu@kcl.ac.uk)
- Bowen Zhu (bowen.zhu@kcl.ac.uk)
- Tengyu Su (tengyu.sun@kcl.ac.uk)
- Jingyi Wang (jingyi.5.wang@kcl.ac.uk)
- Baiyu Liu (baiyu.liu@kcl.ac.uk)
- Shijia Xu (shijia.xu@kcl.ac.uk)

## Short Description
This software is designed to help users track their spending and manage their budget effectively. Set a limit for the budget, track the spending and see where the money is going.

## Project structure
The project is called `NewHappy`. It currently consists of a single app `pst`(Personal Spending Tracker) where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[https://newhappy233.herokuapp.com/]>*.

To login as an administrator, go to <[https://newhappy233.herokuapp.com/admin/]>. Administrator account and password are given in Seed Documentation.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`

## Reference List
1. display forms in modal: https://getbootstrap.com/docs/5.3/components/modal/#how-it-works
2. UI Design Software: https://www.figma.com/file/jDj72Y4uRZvLfLLkMNpNQQ/Personal-Spending-Tracker?node-id=0-1&t=PKtTdIEeHb0jUHUW-0
3. login with google account: https://www.youtube.com/watch?v=56w8p0goIfs
4. How to dockerise Django application: https://www.youtube.com/watch?v=W5Ov0H7E_o4&t=978s
5. Deploy Django Docker Image to Heroku: https://www.youtube.com/watch?v=Oy71OgKZbOQ&t=3600s
6. add static file in heroku: https://stackoverflow.com/questions/68965981/django-static-files-when-hosting-in-heroku
7. spending report charts: https://www.chartjs3.com/docs/chart/getting-started/
8. processing url for sort and filter functions: https://www.youtube.com/watch?v=uwWmvGDHS-8&list=PLWTW5qCM-AkRDmoDJ0E-agVYufq1CtSZh&index=5
9. setting up spending calendar: https://github.com/RTopolowski/SEG-Small_Group_Project

# NewHappy
