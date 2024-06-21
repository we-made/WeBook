export class SelectComponent {
    constructor (element_id, options) {
        if (element_id instanceof Node) {
          this.element = element_id;
          this.$element = $(element_id)
          this.element_id = this.element.getAttribute("id");
        }
        else {
          this.element = document.getElementById(this.element_id);
          this.element_id = element_id
          this.$element = $('#' + element_id);
        }

        this.options = options
    }

    insert_options () {
        let carriedValue = this.$element.val();

        for (let [key, value] of this.options) {
            let option = document.createElement('option');
            option.setAttribute("value", key);
            option.innerText = value;

            this.element.append(option);
        }

        if (carriedValue !== undefined) {
          this.$element.val(carriedValue);
        }
    }

    set_selected(value) {
      let jqObj = null;
      
      if (this.element instanceof Node) {
        jqObj = $(this.element)
      }
      else {
        jqObj = $("#" + this.element);
      }

      jqObj.val(value).change();
    }
}

export class MonthSelectComponent extends SelectComponent {
    constructor (element_id) {
        let options = new Map([
          ["1", 'Januar'],
          ["2", 'Februar'],
          ["3", 'Mars" %}'],
          ["4", 'April'],
          ["5", 'Mai'],
          ["6", 'Juni'],
          ["7", 'Juli'],
          ["8", 'August'],
          ["9", 'September'],
          ["10", 'Oktober'],
          ["11", 'November'],
          ["12", 'Desember'],
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