import RoleBadge from "./role_badge.js";


export default {
  components: {
    RoleBadge
  },
  props: {
    user: Object
  },
  computed: {
    usersActiveRolesMap() {
      return new Map([
        this.user.groups.map( (group) => { [ group, true ] } )
      ]);
    },
    lastLogin() {
      if (!this.user.last_login) {
        return "Aldri logget inn";
      }

      return this.user.last_login;
    }
  },
  methods: {
    openViewMoreDialog() {
      this.$emit("triggerViewMoreDialog", this.user.slug, this.user.name);
    }
  },
  template: `
  <div class="card">
    <div class="card-body border">
      <div style="display: flex; important !important; justify-content: space-between;">
    
        <div>
            <h4>{{user.name}}</h4>
            <h5>{{user.email}}</h5>

            <role-badge
              v-if="user.is_superuser === true"
              class="badge-danger">
              System Administrator
            </role-badge>
            <role-badge
              v-else-if="usersActiveRolesMap.has('planner')"
              class="badge-primary">
              Planlegger
            </role-badge>
            <role-badge
              v-else
              class="badge-light">
              Lesetilgang
            </role-badge>
            
            <div>
                <button class="btn btn-primary wb-btn-main wb-sm btn-sm mt-3"
                    @click="openViewMoreDialog">
                    Vis mer
                </button>
            </div>
        </div>

        <div>
            <div class="alert alert-success p-1 text-center">
                <i class="fas fa-check"></i> Er aktiv
            </div>

            <div>
                <small>
                    <strong>Registrert: </strong>
                    {{user.date_joined}}
                </small>
            </div>
            <div>
                <small>
                    <strong>Sist sett: </strong>
                    {{lastLogin}}
                </small>
            </div>
        </div>
    </div>
    </div>
  </div>
  `
}