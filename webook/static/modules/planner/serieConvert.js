export function serieConvert(serie, formData, keyPrefix=`manifest.`) {
    formData.append(`${keyPrefix}pattern`, serie.pattern.pattern_type);
    formData.append(`${keyPrefix}patternRoutine`, serie.pattern.pattern_routine);
    formData.append(`${keyPrefix}timeAreaMethod`, serie.time_area.method_name);
    formData.append(`${keyPrefix}startDate`, serie.time_area.start_date);
    formData.append(`${keyPrefix}startTime`, serie.time.start);
    formData.append(`${keyPrefix}endTime`, serie.time.end);
    formData.append(`${keyPrefix}ticketCode`, serie.time.ticket_code);
    formData.append(`${keyPrefix}expectedVisitors`, serie.time.expected_visitors);
    formData.append(`${keyPrefix}title`, serie.time.title);
    formData.append(`${keyPrefix}title_en`, serie.time.title_en);

    formData.append(`${keyPrefix}rooms`, serie.rooms);
    formData.append(`${keyPrefix}people`, serie.people);
    formData.append(`${keyPrefix}display_layouts`, serie.display_layouts.split(","));

    debugger;

    switch(serie.pattern.pattern_type) {
        case "daily":
            if (serie.pattern.pattern_routine === "daily__every_x_day") {
                formData.append(`${keyPrefix}interval`, serie.pattern.interval);
            }
            break;
        case "weekly":
            formData.append(`${keyPrefix}interval`, serie.pattern.week_interval);
            var count = 0;
            for (var day of ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) {
                formData.append(`${keyPrefix}${day}`, serie.pattern.days.get(count));
                count++;
            }
            break;
        case "monthly":
            switch (serie.pattern.pattern_routine) {
                case "month__every_x_day_every_y_month":
                    formData.append(`${keyPrefix}interval`, serie.pattern.interval);
                    formData.append(`${keyPrefix}day_of_month`, serie.pattern.day_of_month);
                    break;
                case "month__every_arbitrary_date_of_month":
                    formData.append(`${keyPrefix}arbitrator`, serie.pattern.arbitrator);
                    formData.append(`${keyPrefix}day_of_week`, serie.pattern.weekday);
                    formData.append(`${keyPrefix}interval`, serie.pattern.interval);
                    break;
            }
            break;
        case "yearly":
            formData.append(`${keyPrefix}interval`, serie.pattern.year_interval);
            switch (serie.pattern.pattern_routine) {
                case "yearly__every_x_of_month":
                    formData.append(`${keyPrefix}day_of_month`, serie.pattern.day_index);
                    formData.append(`${keyPrefix}month`, serie.pattern.month);
                    break;
                case "yearly__every_arbitrary_weekday_in_month":
                    formData.append(`${keyPrefix}day_of_week`, serie.pattern.weekday);
                    formData.append(`${keyPrefix}month`, serie.pattern.month);
                    formData.append(`${keyPrefix}arbitrator`, serie.pattern.arbitrator);
                    break;
            }
            break;
    }
    
    if (serie.time_area.stop_within !== undefined) {
        formData.append(`${keyPrefix}stopWithin`, serie.time_area.stop_within);
    }
    if (serie.time_area.instances !== undefined) {
        formData.append(`${keyPrefix}stopAfterXInstances`, serie.time_area.instances);
    }
    if (serie.time_area.projectionDistanceInMonths !== undefined) {
        formData.append(`${keyPrefix}projectionDistanceInMonths`, serie.time_area.projectionDistanceInMonths);
    }

    return formData;
}