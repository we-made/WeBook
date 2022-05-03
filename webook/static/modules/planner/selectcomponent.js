export class SelectComponent {
    constructor (element_id, options) {
        this.$element = $('#' + element_id);
        this.element = document.getElementById(this.element_id);
        this.element_id = element_id
        this.options = options
    }

    insert_options () {
        var carriedValue = this.$element.val();

        for (let [key, value] of this.options) {
            let option = document.createElement('option');
            option.setAttribute("value", key);
            option.innerText = value;
            document.getElementById(this.element_id).append(option);
        }

        if (carriedValue !== undefined) {
          this.$element.val(carriedValue);
        }
    }

    set_selected(value) {
      $("#" + this.element_id).val(value).change();
    }
}

export class MonthSelectComponent extends SelectComponent {
    constructor (element_id) {
        let options = new Map([
          ["1", '{% trans "january" %}'],
          ["2", '{% trans "februar" %}'],
          ["3", '{% trans "march" %}'],
          ["4", '{% trans "april" %}'],
          ["5", '{% trans "may" %}'],
          ["6", '{% trans "june" %}'],
          ["7", '{% trans "july" %}'],
          ["8", '{% trans "august" %}'],
          ["9", '{% trans "september" %}'],
          ["10", '{% trans "october" %}'],
          ["11", '{% trans "november" %}'],
          ["12", '{% trans "december" %}'],
        ]);

        super(element_id, options)

        this.insert_options();
    }
}

export class YearSelectComponent extends SelectComponent {
  constructor ({ element_id, breadth, focusYear } = {}) {

    let options = new Map();
    let years = [];

    for (let i = 0; i < breadth; i++) {
      years.push((focusYear + i), (focusYear + i));
      years.push((focusYear - i), (focusYear - 1));
    }

    years = years.sort();
    years.forEach( (item) => {
      options.set(item, item)
    })

    super(element_id, options);
    this.insert_options();
    this.set_selected(focusYear);
  }
}