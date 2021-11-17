# Calendar Buddy
Crispy for calendars

## Intro
Calendar buddy aims to be, for WeBook calendars, what Crispy is for forms. The gist of the idea behind Calendar Buddy is ease of use,
and to bring a more fully fledged "battery" of sorts to our calendar interactions. 

The core and fundamental design values behind this is:
1. Calendar Buddy should not be married to a specific calendar design plugin -- it should be easy, and intuitive, to consume multiple calendar contexts in a given project. The process should not fundamentally differ (altough the respective implementations will always have differing details)
2. We should be able to programmatically design a calendar from top to bottom - there should be no, or at least as little as possible, complexities in the front end. The complexities that must be handled in the design should be handled in the calendar buddy template (as far as possible). For other things such as callbacks, hooks and events then CalendarBuddy should expose appropriate functionality to allow for consumption.
3. Creating a new calendar should be intuitive and a fluent operation, enhancing readability and giving both front-end developers, as well as back-end developers, an easy facet through which to manipulate the calendar without any language complexity interfering. One should be able to, on a quick glance, understand what is being generated, and how it is being configured.


## Creating a FullCalendar instance

Creating a new FullCalendar instance is quite simple. Simply do this:

```
    calendar_model = calendar_buddy.new_calendar(
        context_type = CalendarBuddy.CalendarContext.FULLCALENDAR
    ).configure_ui(
        view = 0,
        views = ['timeGridWeek'],
        locale = 'nbLocale',
        weekNumbers = true,
        nowIndicator = true,
        allDaySlot = true
    )
```
In your template you would simply then do this:
```
calendar_model | fullcalendar
```
You should now have a FullCalendar instance rendered. While the instancing process does demand some knowledge most of this knowledge is concerning the context, not CalendarBuddy. 

configure_ui simply takes a dict, altough you should be aware that in the context of fullcalendar we want the index of the desired view in "Views" as "View". This is a deviation from the standard fullcalendar behaviour of wanting a string in the "View" option. 
