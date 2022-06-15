/**
 * serie_meta_translator.js
 * Utility for translating a serie into a digestible human readable summary
 */

const WEEKDAY_MAP = new Map([
    [1, "mandag"],
    [2, "tirsdag"],
    [3, "onsdag"],
    [4, "torsdag"],
    [5, "fredag"],
    [6, "lørdag"],
    [0, "søndag"],
]);

const ARBITRATOR_MAP = new Map([
    ["0", "første"],
    ["1", "andre"],
    ["2", "tredje"],
    ["3", "fjerde"],
    ["4", "siste"],
])

const MONTH_MAP = new Map([
    ["1", 'januar'],
    ["2", 'februar'],
    ["3", 'mars'],
    ["4", 'april'],
    ["5", 'mai'],
    ["6", 'juni'],
    ["7", 'juli}'],
    ["8", 'august'],
    ["9", 'september'],
    ["10", 'oktober'],
    ["11", 'november'],
    ["12", 'desember'],
])

const GENERATION_FUNCTIONS_FOR_PATTERNS_MAP = new Map([
    ["daily__every_x_day", (serie) => `Daglig hver ${serie.pattern.interval} dag`],
    ["daily__every_weekday", (serie) => `Hver ukedag`],
    ["weekly__standard", (serie) => `Ukentlig hver ${getDaysStringFromDaysMap(serie.pattern.days)}`],
    ["month__every_x_day_every_y_month", (serie) => `Den ${serie.pattern.day_of_month} hver ${serie.pattern.interval} måned`],
    ["month__every_arbitrary_date_of_month", (serie) => `Hver ${ARBITRATOR_MAP.get(serie.pattern.arbitrator)} ${WEEKDAY_MAP.get(parseInt(serie.pattern.weekday))} hver ${serie.pattern.interval} måned`],
    ["yearly__every_x_of_month", (serie) => `Den ${serie.pattern.year_interval} i ${MONTH_MAP.get(serie.pattern.month)} hvert ${serie.pattern.year_interval} år`],
    ["yearly__every_arbitrary_weekday_in_month", (serie) => `Den ${ARBITRATOR_MAP.get(serie.pattern.arbitrator)} ${WEEKDAY_MAP.get(parseInt(serie.pattern.weekday))} i ${MONTH_MAP.get(serie.pattern.month)} hvert ${serie.pattern.year_interval} år`],
])

const GENERATION_FUNCTIONS_FOR_TIME_AREAS_MAP = new Map([
    ["StopWithin", (serie) => `mellom ${serie.time_area.start_date} og ${serie.time_area.stop_within}`],
    ["StopAfterXInstances", (serie) => `etter ${serie.time_area.instances} forekomst(er)`],
    ["NoStopDate", (serie) => `for evig (projiser ${serie.time_area.projectionDistanceInMonths} måned frem i tid)`],
])

function getDaysStringFromDaysMap(daysMap) {
    return Array.from(daysMap)
        .filter(x => x[1] === true)
        .map(x => WEEKDAY_MAP.get(x[0]))
        .join(", ")
        .replace(/(,)(?!.*\1)/, " og");
}

export class SerieMetaTranslator {
    static generate(serie) {
        return `${(GENERATION_FUNCTIONS_FOR_PATTERNS_MAP.get(serie.pattern.pattern_routine))(serie)} 
                ${(GENERATION_FUNCTIONS_FOR_TIME_AREAS_MAP.get(serie.time_area.method_name))(serie)}`;
    }
}