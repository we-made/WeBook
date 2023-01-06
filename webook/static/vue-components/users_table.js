export default {
    props: {
        users: Array,
    },
    data() {
        return {
            page: 1,
            pageSize: 25,
            checkedUsers: [],
            isBatchMenuCollapsed: false,
            options: [
                {
                    name: "Rediger",
                    slug: "edit"
                }
            ]
        }
    },
    computed: {
        usersMap() {
            return new Map([
                users.map( (user) => [ user.slug, user ] )
            ]);
        },
        visibleUsers() {
            return this.users.slice((this.page - 1) * this.pageSize, this.page * this.pageSize );
        },
        showBatchOptions() {
            return this.checkedUsers.length > 0;
        },
        totalPages() {
            return Math.ceil(this.users.length / this.pageSize)
        },
    },
    watch: {
        users() { this.checkedUsers = []; }
    },
    methods: {
        closeAllDropdowns() {
            console.log(document.querySelectorAll(".dropdown.show"))
            document.querySelectorAll(".dropdown-menu.show").forEach( (element) => { element.classList.toggle("show"); } )
        },
        handleClickUserRow(event, user) {
            console.log(this.$refs)
            console.log(this.$refs.vueSimpleContextMenu.showMenu)
            this.$refs.vueSimpleContextMenu.showMenu(event, {});
        },
        openViewMoreDialog(slug, name) {
            this.$emit("triggerViewMoreDialog", slug, name);
        },
        deactivateSelectedUsers() {
            this.$emit("batchDeactivateUsers", this.checkedUsers);
        },
        activateSelectedUsers() {
            this.$emit("batchActivateUsers", this.checkedUsers);
        },
        roleChangeSelectedUsers() {
            this.$emit("batchPromoteUsers", this.checkedUsers);
        },
        activateUserDialog(user) {
            this.$emit("activateUserDialog", user);
        },
        deactivateUserDialog(user) {
            this.$emit("deactivateUserDialog", user);
        },
        uncheck(index) {
            this.checkedUsers.splice(index, 1);
        },
        toggleBatchOperationMenuBodyCollapse() {
            this.isBatchMenuCollapsed = !this.isBatchMenuCollapsed
        },
        toggleUserCheckState(user) {
            const index = this.checkedUsers.indexOf(user);

            if (index === -1)
                this.checkedUsers.push(user);
            else
                this.uncheck(index);
        },
        uncheckAllUsers() {
            this.checkedUsers = [];
        },
    },
    template: `
        <label class="fw-bold mt-2">Synlige rader:</label>
        <select class='select form-control w-auto' v-model="pageSize">
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
        </select>
        
        <div class="bg-light rounded-top border-start border-top border-end border-dark shadow-5" style="position: -webkit-sticky; position: fixed; bottom: 0px; right: 10%; z-index: 10000;"
             v-if="showBatchOptions === true">
             <div class="wb-bg-main p-2 text-white text-center" @click="toggleBatchOperationMenuBodyCollapse">
                <i class='fas fa-cogs'></i>&nbsp;

                <span class="badge badge-white" v-if="isBatchMenuCollapsed === true">{{ checkedUsers.length }}</span>

                Batch Operations
                <span class='ms-3' @click.stop="toggleBatchOperationMenuBodyCollapse"
                    data-toggle='tooltip' title='Kollaps menyen'>
                    <i class='fas fa-chevron-down' v-if="isBatchMenuCollapsed === false"></i>
                    <i class='fas fa-chevron-up' v-else></i>
                </span>
                <span class='ms-3' @click.stop="uncheckAllUsers"
                        data-toggle='tooltip' title='Avbryt operasjonen'>
                    <i class='fas fa-times'></i>
                </span>
            </div> 
             
            <div class="p-2" v-if="isBatchMenuCollapsed === false">
                <div>
                    <div
                        class="badge badge-light text-dark d-block"
                        v-for="(user, index) in checkedUsers">
                        {{user.name}}
                        <span class="float-end" @click="uncheck(index)"><i class='fas fa-times'></i></span>
                    </div>
                </div>

                <div class="text-center">
                    <small><strong>{{ checkedUsers.length }}</strong> brukere valgt</small>
                </div>
                
                <button class="btn wb-btn-secondary border btn-md btn-block shadow-0" @click="roleChangeSelectedUsers">Endre gruppe</button>

                <div class="row mt-2">
                    <div class="col-lg-6 col-md-6 col-sm-12">
                        <button class="btn wb-btn-secondary border btn-md btn-block shadow-0" @click="deactivateSelectedUsers">
                            Deaktiver
                        </button>
                    </div>
                    <div class="col-lg-6 col-md-6 col-sm-12">
                        <button class="btn wb-btn-secondary border btn-md btn-block shadow-0" @click="activateSelectedUsers">
                            Aktiver
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <table class="table datatable activeTable" id='usersTable'>
            <thead>
                <tr>
                    <th></th>
                    <th>Navn</th>
                    <th>E-Post</th>
                    <th>Tilgangsnivå</th>
                    <th>Sist innlogget</th>
                    <th>Registrert</th>
                    <th>Aktiv?</th>
                    <th>Valg</th>
                </tr>
            </thead>
            <tbody>
                <tr
                    @contextmenu.prevent.stop="handleClickUserRow($event, user)"
                    @click="toggleUserCheckState(user)"
                    v-for="user in visibleUsers.values()">

                    <td> <input type="checkbox" :value="user" v-model="checkedUsers" /> </td>
                    <td>{{user.name}}</td>
                    <td>{{user.email}}</td>
                    <td>
                        <span class="badge badge-danger" v-if="user.is_superuser === true"><i class='fas fa-user-shield'></i>&nbsp; Systemadministrator</span>
                        <span class="badge badge-primary" v-else-if="user.groups.length > 0 && user.groups[0] == 'planners'"><i class='fas fa-eye'></i>&nbsp; Planlegger</span>
                        <span class="badge badge-light" v-else><i class='fas fa-eye'></i>&nbsp; Lesetilgang</span>
                    </td>
                    <td>{{user.last_login}}</td>
                    <td>{{user.date_joined}}</td>
                    <td>
                        <i class="fas fa-check text-success" v-if="user.is_active === true"></i>
                        <i class="fas fa-times text-danger" v-else></i>
                    </td>
                    <td>
                        <div class='btn-group shadow-0'>
                            <button 
                                class="btn wb-btn-main wb-btn-sm p-1 ps-2 pe-2"
                                @click.stop="openViewMoreDialog(user.slug, user.name)">
                                Rediger
                            </button>
                            <button 
                                @click.stop="closeAllDropdowns"
                                class="btn wb-btn-main wb-btn-sm p-1 ps-2 pe-2 dropdown-toggle dropdown-toggle-split"
                                data-mdb-toggle="dropdown"
                                aria-expanded="false"
                                type="button">
                                <!--<i class='fas fa-ellipsis-v'></i>-->
                            </button>
                            <ul class="dropdown-menu">
                                <li> <a class="dropdown-item" @click.stop="() => { openViewMoreDialog(user.slug, user.name); closeAllDropdowns(); }"> <i class='fas fa-edit'></i> Rediger</a> </li>
                                <li v-if="user.is_active === true" @click.stop="() => { deactivateUserDialog(user); closeAllDropdowns(); }"> <a class="dropdown-item"> <i class='fas fa-times text-danger'></i> Deaktiver</a> </li>
                                <li v-else> <a class="dropdown-item" @click.stop="() => { activateUserDialog(user); closeAllDropdowns(); }"> <i class='fas fa-check text-success'></i> Aktiver</a> </li>
                            </ul>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>


    <vue-simple-context-menu
        :options="options"
        ref="vueSimpleContextMenu"
        @option-clicked="optionClicked"
    />

    <nav aria-label="Table pagination or navigation" class="clearfix">
        <ul class="pagination float-end">
            <li class="page-item" :class="{ disabled: page == 1 }"><a class="page-link" href="javascript:void(0)" @click.stop="page--">Forrige</a></li>
            <li class="page-item" :class="{ active: thisPage == page }" v-for="thisPage in totalPages"><a class="page-link" @click.stop="page = thisPage">{{thisPage}}</a></li>
            <li class="page-item" :class="{ disabled: page == totalPages }"><a class="page-link" href="javascript:void(0)" @click.stop="page++">Neste</a></li>
        </ul>
    </nav>
    `
}