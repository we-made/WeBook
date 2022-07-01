
class DateExtensions {
    /* Overwrite the time values for one Date instance with the value of a time field (as a str) */
    static OverwriteDateTimeWithTimeInputValue(date_to_write_time_to, time_input_val_as_str) {

        let times = time_input_val_as_str.split(':');
        let date = new Date(date_to_write_time_to);

        date.setHours(times[0]);
        date.setMinutes(times[1]);

        return date;
    }
}

Date.prototype.addDays = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}

/**
 * Utility class primarily intended to wrap around the various strategies employed in the
 * series util, offering a far more succinct and consumable vector for executing the strategies, as well
 * as constructing parameter bodies.
 */
 class StrategyExecutorAbstraction {
    constructor ({function_to_run, parameter_obj}={}) {
        this.function_to_run = function_to_run

        this.parameters = {}
        if (parameter_obj !== undefined) {
            this.add_object_keyvals_as_params(parameter_obj);
        }
    }

    add_object_keyvals_as_params(obj) {
        for (let [key, value] of Object.entries(obj)) {
            this.parameters[key] = value;
        }
    }

    run(extra_params=undefined) {
        if (extra_params !== undefined) {
            this.add_object_keyvals_as_params(extra_params);
        }

        return this.function_to_run(this.parameters);
    }
}

/**
     * Series util logic for calculating series of events in given patterns. Dynamically extensible, and split up into three chief
     * components; the strategy, the recurrence pattern and the cycle.
     * @inner
     */
 export class SeriesUtil {

    static calculate_serie (serie) {
        const pattern_strategies = new Map();
        pattern_strategies.set(
            "daily__every_x_day",
            new StrategyExecutorAbstraction({
                function_to_run: this.daily__every_x_day,
                parameter_obj: serie.pattern
            })
        );
        pattern_strategies.set(
            "daily__every_weekday",
            new StrategyExecutorAbstraction({
                function_to_run: this.daily__every_weekday,
                parameter_obj: {},
            })
        );
        pattern_strategies.set(
            "weekly__standard",
            new StrategyExecutorAbstraction({
                function_to_run: this.weekly_standard,
                parameter_obj: serie.pattern,
            })
        );
        pattern_strategies.set(
            "month__every_x_day_every_y_month",
            new StrategyExecutorAbstraction({
                function_to_run: this.month__every_x_day_every_y_month,
                parameter_obj: serie.pattern,
            })
        );
        pattern_strategies.set(
            "month__every_arbitrary_date_of_month",
            new StrategyExecutorAbstraction({
                function_to_run: this.month__every_arbitrary_date_of_month,
                parameter_obj: serie.pattern,
            }));
        pattern_strategies.set(
            "yearly__every_x_of_month",
            new StrategyExecutorAbstraction({
                function_to_run: this.yearly__every_x_of_month,
                parameter_obj: serie.pattern,
            })
        );
        pattern_strategies.set(
            "yearly__every_arbitrary_weekday_in_month",
            new StrategyExecutorAbstraction({
                function_to_run: this.yearly__every_arbitrary_weekday_in_month,
                parameter_obj: serie.pattern,
            })
        );

        const area_strategies = new Map();
        area_strategies.set(
            "StopWithin",
            new StrategyExecutorAbstraction(
                {
                    function_to_run: this.area__stop_within,
                    parameter_obj: {
                        stop_within_date: DateExtensions.OverwriteDateTimeWithTimeInputValue(serie.time_area.stop_within, "23:59")
                    }
                }
            )
        );
        area_strategies.set(
            "StopAfterXInstances",
            new StrategyExecutorAbstraction(
                {
                    function_to_run: this.area__stop_after_x_instances,
                    parameter_obj: serie.time_area,
                }
            )
        );
        area_strategies.set(
            "NoStopDate",
            new StrategyExecutorAbstraction(
                {
                    function_to_run: this.area__no_stop_date,
                    parameter_obj: serie.time_area,
                }
            )
        );

        let area_strategy = area_strategies.get(serie.time_area.method_name);
        let scope = area_strategy.run({ start_date: serie.time_area.start_date });

        let pattern_strategy = pattern_strategies.get(serie.pattern.pattern_routine);

        let events = [];

        let date_cursor = scope.start_date;
        let instance_cursor = 0;
        let cycle_cursor = 0;

        let event_sample = {
            title: serie.time.title,
            start: serie.time.start,
            end: serie.time.end,
            color: serie.time.color,
        }
        while ((scope.stop_within_date !== undefined && date_cursor < scope.stop_within_date) || (scope.instance_limit !== 0 && scope.instance_limit >= instance_cursor)) {

            /*
                There are two ways we monitor our "progress" here. One is by the date cursor, and one is by instances.
                In some cases we only want to do the repetition pattern until a set date, other times we wish do it X times.
                Hence we need to have this "cycle manager" to handle the repeating for us - and alleviate the strategies from
                having to concern themselves with this. This in turn means that a repetition pattern/strategy is run in cycles - as one may see in their
                respective implementations, and this does to some degree dictate implementations.
                This does put the onus of managing the end of the series/repetition on the cycle manager (which is what this is.)
            */
            event_sample = Object.assign({}, event_sample);
            let result = pattern_strategy.run({cycle: cycle_cursor, start_date: date_cursor, event: event_sample});

            if (result === undefined || (Array.isArray(result) && result.length == 0)) {
                cycle_cursor++;
                continue;
            }

            if (scope.stop_within_date !== undefined && result.from >= scope.stop_within_date ||
                scope.instance_limit !== undefined && scope.instance_limit !== undefined && instance_cursor > scope.instance_limit) {
                break;
            }

            let move_cursor_to = date_cursor
            if (Array.isArray(result)) {
                move_cursor_to = result[result.length - 1].to
            }
            else {
                move_cursor_to = result.to
            }

            date_cursor = move_cursor_to
            date_cursor = date_cursor.addDays(1)

            if (scope.instance_limit !== 0) {
                instance_cursor++;
            }

            if (Array.isArray(result)) {
                events = events.concat(result);
            }
            else {
                events.push(result);
            }

            cycle_cursor++;
        }

        if (serie.time_area.method_name == "StopWithin")
            this.custom__prevent_spillover(events, scope.stop_within_date, serie.time_area.method_name)

        return events;
    }

    static custom__prevent_spillover(events, stop_within_date) {
         /*
                This function prevents undesired spill over of dates when StopWithin method used in area of reccurence
         */
        for (let i = events.length - 1; i >= 0; i--) {
            if (events[i].to>stop_within_date)
                events.splice(i, 1);
        }
    }

    static area__stop_within({start_date, stop_within_date} = {}) {
        return {
            start_date: new Date(start_date),
            stop_within_date: new Date(stop_within_date),
            instance_limit: 0,
        }
    }

    static area__stop_after_x_instances({start_date, instances} = {}) {
        return {
            start_date: new Date(start_date),
            stop_within_date: undefined,
            instance_limit: instances,
        }
    }

    static area__no_stop_date({start_date, projectionDistanceInMonths} = {}) {
        start_date = new Date(start_date)

        let stop_within_date = new Date(start_date)
        let month = start_date.getMonth();
        stop_within_date.setMonth(parseInt(month) + parseInt(projectionDistanceInMonths));
        return {
            start_date: start_date,
            stop_within_date: stop_within_date,
            instance_limit: 0
        }
    }

    static daily__every_x_day({cycle, start_date, event, interval}={}) {
        if (cycle != 0) {
            start_date = start_date.addDays(interval - 1); // -1 to account for the "move-forward" padding done in cycler
        }

        event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.start);
        event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.end);

        return event;
    }

    static daily__every_weekday({cycle, event, start_date}={}) {
        while ([0,6].includes(start_date.getDay())) {
            start_date = start_date.addDays(1);
        }

        event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.start);
        event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.end);

        return event;
    }

    static weekly_standard({cycle, start_date, event, week_interval, days}={}) {
        if (cycle != 0) {
            /*
            We need to make sure that we always work with monday as base excepting when we are running the first cycle (0), as
            the user can specify a start_date in the middle of a week. The end, as is the standard in the other strategies, is
            the responsibility of the cycle runner, so we don't care about that here.
            */
            if (start_date.getDay() !== 1) {
                if (start_date.getDay != 0) {
                    start_date = start_date.addDays( (start_date.getDay() - 1) * -1)
                }
                else if (start_date.getDay == 0) {
                    start_date = start_date.addDays(1)
                }
            }

            start_date = start_date.addDays(7 * parseInt(week_interval))
        }

        let events = [];
        let y = 0;
        for (let i = start_date.getDay(); i < 6; i++) {
            let day = days.get(i)
            if (day === true) {
                let adjusted_date = (new Date(start_date)).addDays(y);
                let ev_copy = Object.assign({}, event);
                ev_copy.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.start)
                ev_copy.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.end);

                events.push(ev_copy);
            }

            y++;
        }

        return events;
    }

    static month__every_x_day_every_y_month({cycle, start_date, day_of_month, event, interval}={}) {
        if (cycle !== 0)  {
            start_date.setMonth(start_date.getMonth() + parseInt(interval))
            start_date.setDate(1);
        }

        if (day_of_month > start_date.getDate()) {
            return;
        }

        let adjusted_date = (new Date(start_date)).setDate(day_of_month);
        event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.start);
        event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.end);

        return event;
    }

    static arbitrator_find(start_date, arbitrator, weekday) {
       // helps us parse from 1,2,3,4,5,6,7 to 0,1,2,3,4,5,6 that JS uses
       let weekDayParseReverseMap = new Map([
           [0, 7],
           [6, 6],
           [5, 5],
           [4, 4],
           [3, 3],
           [2, 2],
           [1, 1],
       ]);

       // Before we can do anything we need to find the first occurrence of weekday
       // in the month

       let month = start_date.getMonth();

       let date = new Date(start_date);
       date.setDate(1);
       let first_weekday_of_month = date.getDay();
       if (weekDayParseReverseMap.get(first_weekday_of_month) > weekday) { // not present in first week, go to second
           date = date.addDays(7);
       }

       // go to the first instance of weekday
       let weekdaydiff = parseInt(weekDayParseReverseMap.get(date.getDay())) - parseInt(weekday);
       date = date.addDays(weekdaydiff * -1);

       // go to the desired position, as determined by the arbitrator (is that even the right word? :D)
       date = date.addDays(arbitrator * 7);
       if (arbitrator == 5) {
           if (date.getMonth() !== month) { // last instance of weekday is in week 4
               date = date.addDays(4 * 7);
           }
       }

       return date;
    }

    static month__every_arbitrary_date_of_month({cycle, event, start_date, arbitrator, weekday, interval}={}) {
        if (cycle != 0) {
            start_date.setDate(1);
            let month = start_date.getMonth();
            start_date.setMonth(month + parseInt(interval));
        }

        let date = SeriesUtil.arbitrator_find(start_date, arbitrator, weekday);
        event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.start);
        event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.end)

        return event;
    }

    static yearly__every_x_of_month ({cycle, start_date, event, day_index, year_interval, month}={}) {
        if (cycle !== 0)  {
            start_date.setFullYear ( start_date.getFullYear() + parseInt(year_interval) )
        }

        let date = new Date(start_date.getFullYear() + "-" + month + "-" + day_index);
        event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.start);
        event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.end);

        return event;
    }

    static yearly__every_arbitrary_weekday_in_month ({cycle, start_date, event, arbitrator, weekday, year_interval, month}={}) {
        if (cycle != 0) {
            start_date.setFullYear ( start_date.getFullYear() + parseInt(year_interval) )
        }

        let date = new Date(start_date.getFullYear() + "-" + month + "-01");

        // use the "day-seek" algo to find the correct day, according to the arbitrator
        date = SeriesUtil.arbitrator_find(date, arbitrator, weekday);

        event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.start);
        event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.end);

        return event;
    }
};
