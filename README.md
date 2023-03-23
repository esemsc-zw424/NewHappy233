# Team NewHappy Large Group project

# Title of project and the name of the software
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
The application 

## Project structure
The project is called `NewHappy`. It currently consists of a single app `pst`(Personal Spending Tracker) where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[](URL)>*.

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

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

## Reference List
1. display forms in modal: https://getbootstrap.com/docs/5.3/components/modal/#how-it-works
2. UI Design Software: https://www.figma.com/file/jDj72Y4uRZvLfLLkMNpNQQ/Personal-Spending-Tracker?node-id=0-1&t=PKtTdIEeHb0jUHUW-0
3. spending report charts: https://www.chartjs3.com/docs/chart/getting-started/
4. processing url for sort and filter functions: https://www.youtube.com/watch?v=uwWmvGDHS-8&list=PLWTW5qCM-AkRDmoDJ0E-agVYufq1CtSZh&index=5


# NewHappy
