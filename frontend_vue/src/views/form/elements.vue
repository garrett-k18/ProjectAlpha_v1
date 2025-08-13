<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Input Types">
          <template v-slot:sub-text>
            Most common form control, text-based input fields. Includes
            support for all HTML5 types: <code>text</code>,
            <code>password</code>, <code>datetime</code>,
            <code>datetime-local</code>, <code>date</code>,
            <code>month</code>, <code>time</code>, <code>week</code>,
            <code>number</code>, <code>email</code>, <code>url</code>,
            <code>search</code>, <code>tel</code>, and <code>color</code>.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <b-form>
                  <b-form-group
                      label="Text"
                      label-for="simpleinput"
                      class="mb-3"
                  >
                    <b-form-input type="text" id="simpleinput"/>
                  </b-form-group>

                  <b-form-group
                      label="Email"
                      label-for="example-email"
                      class="mb-3"
                  >
                    <b-form-input
                        type="email"
                        id="example-email"
                        name="example-email"
                        placeholder="Email"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Password"
                      label-for="example-password"
                      class="mb-3"
                  >
                    <b-form-input
                        type="password"
                        id="example-password"
                        value="password"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Show/Hide Password"
                      label-for="password"
                      class="mb-3"
                  >
                    <div class="input-group input-group-merge">
                      <b-form-input
                          type="password"
                          id="password"
                          placeholder="Enter your password"
                      />
                      <div class="input-group-text" data-password="false">
                        <span class="password-eye"></span>
                      </div>
                    </div>
                  </b-form-group>

                  <b-form-group
                      label="Placeholder"
                      label-for="example-palaceholder"
                      class="mb-3"
                  >
                    <b-form-input
                        type="text"
                        id="example-palaceholder"
                        placeholder="placeholder"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Text area"
                      label-for="example-textarea"
                      class="mb-3"
                  >
                    <b-form-textarea
                        id="example-textarea"
                        rows="5"
                    ></b-form-textarea>
                  </b-form-group>

                  <b-form-group
                      label="Readonly"
                      label-for="example-readonly"
                      class="mb-3"
                  >
                    <b-form-input
                        type="text"
                        id="example-readonly"
                        readonly
                        value="Readonly value"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Disabled"
                      label-for="example-disable"
                      class="mb-3"
                  >
                    <b-form-input
                        type="text"
                        id="example-disable"
                        disabled
                        value="Disabled value"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Static control"
                      label-for="example-static"
                      class="mb-3"
                  >
                    <input
                        type="text"
                        readonly
                        class="form-control-plaintext"
                        id="example-static"
                        value="email@example.com"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Helping text"
                      label-for="example-helping"
                      class="mb-0"
                  >
                    <b-form-input
                        type="text"
                        id="example-helping"
                        placeholder="Helping text"
                    />
                    <span class="help-block"
                    ><small
                    >A block of help text that breaks onto a new line and
                        may extend beyond one line.</small
                    ></span
                    >
                  </b-form-group>
                </b-form>
              </b-col>

              <b-col lg="6">
                <b-form>
                  <b-form-group
                      label="Input Select"
                      label-for="example-select"
                      class="mb-3"
                  >
                    <b-form-select
                        v-model="selected1"
                        :options="options1"
                        class="form-select"
                        id="example-select"
                    >
                    </b-form-select>
                  </b-form-group>

                  <b-form-group
                      label="Multiple Select"
                      label-for="example-multiselect"
                      class="mb-3"
                  >
                    <b-form-select
                        id="example-multiselect"
                        :options="options1"
                        multiple
                    >
                    </b-form-select>
                  </b-form-group>

                  <b-form-group
                      label="Default file input"
                      label-for="example-fileinput"
                      class="mb-3"
                  >
                    <input
                        type="file"
                        id="example-fileinput"
                        class="form-control"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Date"
                      label-for="example-date"
                      class="mb-3"
                  >
                    <b-form-input id="example-date" type="date" name="date"/>
                  </b-form-group>

                  <b-form-group
                      label="Month"
                      label-for="example-month"
                      class="mb-3"
                  >
                    <b-form-input
                        id="example-month"
                        type="month"
                        name="month"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Time"
                      label-for="example-time"
                      class="mb-3"
                  >
                    <b-form-input id="example-time" type="time" name="time"/>
                  </b-form-group>

                  <b-form-group
                      label="Week"
                      label-for="example-week"
                      class="mb-3"
                  >
                    <b-form-input id="example-week" type="week" name="week"/>
                  </b-form-group>

                  <b-form-group
                      label="Number"
                      label-for="example-number"
                      class="mb-3"
                  >
                    <b-form-input
                        id="example-number"
                        type="number"
                        name="number"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Color"
                      label-for="example-color"
                      class="mb-3"
                  >
                    <b-form-input
                        id="example-color"
                        type="color"
                        name="color"
                        class="w-100"
                        value="#727cf5"
                    />
                  </b-form-group>

                  <b-form-group
                      label="Range"
                      label-for="example-range"
                      class="mb-0"
                  >
                    <b-form-input
                        id="example-range"
                        type="range"
                        name="range"
                        min="0"
                        max="100"
                    />
                  </b-form-group>
                </b-form>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Floating labels">
          <template v-slot:sub-text>
            Wrap a pair of <code>&lt;input class="form-control"&gt;</code> and
            <code>&lt;label&gt;</code> elements in
            <code>.form-floating</code> to enable floating labels with
            Bootstrap’s textual form fields. A <code>placeholder</code> is
            required on each <code>&lt;input&gt;</code> as our method of
            CSS-only floating labels uses the
            <code>:placeholder-shown</code> pseudo-element. Also note that the
            <code>&lt;input&gt;</code> must come first so we can utilize a
            sibling selector (e.g., <code>~</code>).
          </template>
          <template v-slot:preview>
            <b-row>
              <b-col lg="6">
                <h5 class="mb-3">Example</h5>
                <div class="form-floating mb-3">
                  <b-form-input
                      type="email"
                      id="floatingInput"
                      placeholder="name@example.com"
                  />
                  <label for="floatingInput">Email address</label>
                </div>
                <div class="form-floating">
                  <b-form-input
                      type="password"
                      id="floatingPassword"
                      placeholder="Password"
                  />
                  <label for="floatingPassword">Password</label>
                </div>

                <h5 class="mb-3 mt-4">Textareas</h5>
                <div class="form-floating">
                  <b-form-textarea
                      placeholder="Leave a comment here"
                      id="floatingTextarea"
                      style="height: 100px"
                  ></b-form-textarea>
                  <label for="floatingTextarea">Comments</label>
                </div>
              </b-col>

              <b-col lg="6">
                <h5 class="mb-3">Selects</h5>
                <div class="form-floating">
                  <b-form-select
                      v-model="selected2"
                      :options="options2"
                      id="floatingSelect"
                      aria-label="Floating label select example"
                  >
                  </b-form-select>
                  <label for="floatingSelect">Works with selects</label>
                </div>

                <h5 class="mb-3 mt-4">Layout</h5>
                <b-row class="g-2">
                  <b-col class="col-md">
                    <div class="form-floating">
                      <b-form-input
                          type="email"
                          id="floatingInputGrid"
                          placeholder="name@example.com"
                          value="mdo@example.com"
                      />
                      <label for="floatingInputGrid">Email address</label>
                    </div>
                  </b-col>
                  <b-col class="col-md">
                    <div class="form-floating">
                      <b-form-select
                          v-model="selected2"
                          :options="options2"
                          id="floatingSelectGrid"
                          aria-label="Floating label select example"
                      >
                      </b-form-select>
                      <label for="floatingSelectGrid">Works with selects</label>
                    </div>
                  </b-col>
                </b-row>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
            <b-row>

              <b-col lg="6">
                <CustomSyntax title="Select">
                  <template v-slot:sub-text>
                    <code>&lt;select&gt;</code> menus need only a custom class,
                    <code>.form-select</code> to trigger the custom styles.
                  </template>
                  <template v-slot:preview>
                    <b-form-select
                        v-model="selected2"
                        :options="options2"
                        class="mb-3"
                    >
                    </b-form-select>
                    <b-form-select
                        v-model="selected2"
                        :options="options2"
                        class="form-select-lg mb-3"
                    >
                    </b-form-select>
                    <b-form-select
                        v-model="selected2"
                        :options="options2"
                        class="form-select-sm mb-3"
                    >
                    </b-form-select>
                    <div class="input-group mb-3">
                      <label class="input-group-text" for="inputGroupSelect01"
                      >Options</label
                      >
                      <b-form-select
                          v-model="selected3"
                          :options="options3"
                          id="inputGroupSelect01"
                      >
                      </b-form-select>
                    </div>
                    <div class="input-group">
                      <b-form-select
                          v-model="selected3"
                          :options="options3"
                          id="inputGroupSelect04"
                          aria-label="Example select with button addon"
                      >
                      </b-form-select>
                      <b-button variant="outline-secondary" type="button">
                        Button
                      </b-button>
                    </div>
                  </template>
                </CustomSyntax>
              </b-col>

              <b-col lg="6">
                <CustomSyntax title="Switches">
                  <template v-slot:sub-text>
                    A switch has the markup of a custom checkbox but uses the
                    <code>.form-switch</code> class to render a toggle switch.
                    Switches also support the <code>disabled</code> attribute.
                  </template>
                  <template v-slot:preview>
                    <b-form-checkbox id="customSwitch1" switch>
                      Toggle this switch element
                    </b-form-checkbox>
                    <div class="mt-1">
                      <b-form-checkbox disabled id="customSwitch2" switch>
                        Disabled switch element
                      </b-form-checkbox>
                    </div>
                  </template>
                </CustomSyntax>
              </b-col>

            </b-row>
      </b-col>
    </b-row>

    <b-row>
      <b-col lg="6">

        <CustomSyntax title="Checkboxes">
          <template v-slot:sub-text>
            Each checkbox and radio <code>&lt;input&gt;</code> and
            <code>&lt;label&gt;</code> pairing is wrapped in a
            <code>&lt;div&gt;</code> to create our custom control.
            Structurally, this is the same approach as our default
            <code>.form-check</code>.
          </template>
          <template v-slot:preview>
            <h6 class="fs-15">Checkboxes</h6>
            <div class="mt-3">
              <b-form-checkbox id="customCheck1"
              >Check this custom checkbox
              </b-form-checkbox
              >

              <b-form-checkbox id="customCheck2"
              >Check this custom checkbox
              </b-form-checkbox
              >
            </div>

            <h6 class="fs-15 mt-3">Inline</h6>
            <div class="mt-2">
              <div class="form-check-inline">
                <b-form-checkbox id="customCheck3"
                >Check this custom checkbox
                </b-form-checkbox
                >
              </div>
              <div class="form-check-inline">
                <b-form-checkbox id="customCheck4"
                >Check this custom checkbox
                </b-form-checkbox
                >
              </div>
            </div>

            <h6 class="fs-15 mt-3">Disabled</h6>

            <div class="mt-2">
              <div class="form-check-inline">
                <b-form-checkbox id="customCheck5" v-model="checked" disabled
                >Check this custom checkbox
                </b-form-checkbox
                >
              </div>
              <div class="form-check-inline">
                <b-form-checkbox id="customCheck6" disabled
                >Check this custom checkbox
                </b-form-checkbox
                >
              </div>
            </div>

            <h6 class="fs-15 mt-3">Colors</h6>

            <div class="mb-2">
              <b-form-checkbox id="customCheckcolor1" v-model="checked"
              >Default Checkbox
              </b-form-checkbox
              >
            </div>
            <div class="form-checkbox-success mb-2">
              <b-form-checkbox id="customCheckcolor2" v-model="checked"
              >Success Checkbox
              </b-form-checkbox
              >
            </div>
            <div class="form-checkbox-info mb-2">
              <b-form-checkbox id="customCheckcolor3" v-model="checked"
              >Info Checkbox
              </b-form-checkbox
              >
            </div>
            <div class="form-checkbox-secondary mb-2">
              <b-form-checkbox id="customCheckcolor6" v-model="checked"
              >Secondary Checkbox
              </b-form-checkbox
              >
            </div>
            <div class="form-checkbox-warning mb-2">
              <b-form-checkbox id="customCheckcolor4" v-model="checked"
              >Warning Checkbox
              </b-form-checkbox
              >
            </div>
            <div class="form-checkbox-danger mb-2">
              <b-form-checkbox id="customCheckcolor5" v-model="checked"
              >Danger Checkbox
              </b-form-checkbox
              >
            </div>
            <div class="form-checkbox-dark">
              <b-form-checkbox id="customCheckcolor7" v-model="checked"
              >Dark Checkbox
              </b-form-checkbox
              >
            </div>
          </template>
        </CustomSyntax>
      </b-col>

      <b-col lg="6">
        <CustomSyntax title="radios">
          <template v-slot:sub-text>
            Each checkbox and radio <code>&lt;input&gt;</code> and
            <code>&lt;label&gt;</code> pairing is wrapped in a
            <code>&lt;div&gt;</code> to create our custom control.
            Structurally, this is the same approach as our default
            <code>.form-check</code>.
          </template>
          <template v-slot:preview>
            <h6 class="fs-15 mt-3">Radios</h6>

            <b-form-group class="mt-3">
              <b-form-radio id="customRadio1" name="customRadio"
              >Toggle this custom radio
              </b-form-radio
              >

              <b-form-radio id="customRadio2" name="customRadio"
              >Or toggle this other custom radio
              </b-form-radio
              >
            </b-form-group>

            <h6 class="fs-15 mt-3">Inline</h6>

            <b-form-group class="mt-2">
              <div class="form-check-inline">
                <b-form-radio id="customRadio3" name="customRadio1"
                >Toggle this custom radio
                </b-form-radio
                >
              </div>
              <div class="form-check-inline">
                <b-form-radio id="customRadio4" name="customRadio1"
                >Or toggle this other custom radio
                </b-form-radio
                >
              </div>
            </b-form-group>

            <h6 class="fs-15 mt-3">Disabled</h6>

            <b-form-group class="mt-2">
              <div class="form-check-inline">
                <b-form-radio id="customRadio5" name="customRadio2" disabled
                >Toggle this custom radio
                </b-form-radio
                >
              </div>
              <div class="form-check-inline">
                <b-form-radio
                    id="customRadio6"
                    name="customRadio2"
                    v-model="checked"
                    disabled
                >Or toggle this other custom radio
                </b-form-radio
                >
              </div>
            </b-form-group>

            <h6 class="fs-15 mt-3">Colors</h6>

            <div class="mb-2">
              <b-form-radio
                  id="customRadiocolor1"
                  name="customRadiocolor1"
                  v-model="checked"
              >Default Radio
              </b-form-radio
              >
            </div>
            <div class="form-radio-success mb-2">
              <b-form-radio
                  id="customRadiocolor2"
                  name="customRadiocolor2"
                  v-model="checked"
              >Success Radio
              </b-form-radio
              >
            </div>
            <div class="form-radio-info mb-2">
              <b-form-radio
                  id="customRadiocolor3"
                  name="customRadiocolor3"
                  v-model="checked"
              >Info Radio
              </b-form-radio
              >
            </div>
            <div class="form-radio-secondary mb-2">
              <b-form-radio
                  id="customRadiocolor6"
                  name="customRadiocolor6"
                  v-model="checked"
              >Secondary Radio
              </b-form-radio
              >
            </div>
            <div class="form-radio-warning mb-2">
              <b-form-radio
                  id="customRadiocolor4"
                  name="customRadiocolor4"
                  v-model="checked"
              >Warning Radio
              </b-form-radio
              >
            </div>
            <div class="form-radio-danger mb-2">
              <b-form-radio
                  id="customRadiocolor5"
                  name="customRadiocolor5"
                  v-model="checked"
              >Danger Radio
              </b-form-radio
              >
            </div>
            <div class="form-radio-dark">
              <b-form-radio
                  id="customRadiocolor7"
                  name="customRadiocolor7"
                  v-model="checked"
              >Dark Radio
              </b-form-radio
              >
            </div>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <b-row>
      <b-col lg="6">
        <CustomSyntax title="Input Sizes">
          <template v-slot:sub-text>
            Set heights using classes like <code>.input-lg</code>, and set
            widths using grid column classes like <code>.col-lg-*</code>.
          </template>
          <template v-slot:preview>
            <b-form>
              <b-form-group
                  label="Small"
                  label-for="example-input-small"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="example-input-small"
                    name="example-input-small"
                    class="form-control-sm"
                    placeholder=".input-sm"
                />
              </b-form-group>

              <b-form-group
                  label="Normal"
                  label-for="example-input-normal"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="example-input-normal"
                    name="example-input-normal"
                    placeholder="Normal"
                />
              </b-form-group>

              <b-form-group
                  label="Large"
                  label-for="example-input-large"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="example-input-large"
                    name="example-input-large"
                    class="form-control-lg"
                    placeholder=".input-lg"
                />
              </b-form-group>

              <b-form-group
                  label="Grid Sizes"
                  label-for="example-gridsize"
                  class="mb-2"
              >
                <b-row>
                  <b-col sm="4">
                    <b-form-input
                        type="text"
                        id="example-gridsize"
                        placeholder=".col-sm-4"
                    />
                  </b-col>
                </b-row>
              </b-form-group>
            </b-form>
          </template>
        </CustomSyntax>

      </b-col>

      <b-col lg="6">
        <CustomSyntax title="Input Group">
          <template v-slot:sub-text>
            Easily extend form controls by adding text, buttons, or button
            groups on either side of textual inputs, custom selects, and
            custom file inputs
          </template>
          <template v-slot:preview>
            <b-form>
              <b-form-group label="Static" class="mb-3">
                <div class="input-group flex-nowrap">
                  <span class="input-group-text" id="basic-addon1">@</span>
                  <b-form-input
                      type="text"
                      placeholder="Username"
                      aria-label="Username"
                      aria-describedby="basic-addon1"
                  />
                </div>
              </b-form-group>

              <b-form-group label="Dropdowns" class="mb-3">
                <div class="input-group">
                  <b-dropdown menu-class="dropdown-menu">
                    <template
                        #button-content
                        class="btn btn-primary"
                        type="button"
                    >
                      Dropdown
                    </template>

                    <b-dropdown-item>Action</b-dropdown-item>
                    <b-dropdown-item>Another action</b-dropdown-item>
                    <b-dropdown-item
                    >Something else here
                    </b-dropdown-item
                    >
                  </b-dropdown>
                  <b-form-input
                      type="text"
                      placeholder=""
                      aria-label=""
                      aria-describedby="basic-addon1"
                  />
                </div>
              </b-form-group>

              <b-form-group label="Buttons" class="mb-3">
                <div class="input-group">
                  <b-form-input
                      type="text"
                      placeholder="Recipient's username"
                      aria-label="Recipient's username"
                  />
                  <b-button variant="dark" type="button">Button</b-button>
                </div>
              </b-form-group>

              <b-row class="g-2">
                <b-col sm="6">
                  <b-form-group label="File input">
                    <input
                        class="form-control"
                        type="file"
                        id="inputGroupFile04"
                    />
                  </b-form-group>
                </b-col>
                <b-col sm="6">
                  <b-form-group
                      label="Multiple files input"
                      label-for="formFileMultiple01"
                  >
                    <input
                        class="form-control"
                        type="file"
                        id="formFileMultiple01"
                        multiple
                    />
                  </b-form-group>
                </b-col>
              </b-row>
            </b-form>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col lg="6">
        <CustomSyntax title="Basic Example">
          <template v-slot:sub-text>
            Here’s a quick example to demonstrate Bootstrap’s form styles.
            Keep reading for documentation on required classes, form layout,
            and more.
          </template>
          <template v-slot:preview>
            <b-form>
              <b-form-group
                  label="Email address"
                  label-for="exampleInputEmail1"
                  class="mb-3"
              >
                <b-form-input
                    type="email"
                    id="exampleInputEmail1"
                    aria-describedby="emailHelp"
                    placeholder="Enter email"
                />
                <small id="emailHelp" class="form-text text-muted"
                >We'll never share your email with anyone else.</small
                >
              </b-form-group>
              <b-form-group
                  label="Password"
                  label-for="exampleInputPassword1"
                  class="mb-3"
              >
                <b-form-input
                    type="password"
                    id="exampleInputPassword1"
                    placeholder="Password"
                />
              </b-form-group>
              <div class="mb-3">
                <b-form-checkbox id="checkmeout0"
                >Check me out !
                </b-form-checkbox
                >
              </div>
              <b-button variant="primary" type="submit">Submit</b-button>
            </b-form>
          </template>
        </CustomSyntax>

      </b-col>

      <b-col lg="6">
        <CustomSyntax title="Horizontal form">
          <template v-slot:sub-text>
            Create horizontal forms with the grid by adding the
            <code>.row</code> class to form groups and using the
            <code>.col-*-*</code> classes to specify the width of your labels
            and controls. Be sure to add <code>.col-form-label</code> to your
            <code>&lt;label&gt;</code>s as well so they’re vertically centered
            with their associated form controls.
          </template>
          <template v-slot:preview>
            <b-form class="form-horizontal">
              <b-row class="mb-3">
                <label for="inputEmail3" class="col-3 col-form-label"
                >Email</label
                >
                <b-col cols="9">
                  <b-form-input
                      type="email"
                      id="inputEmail3"
                      placeholder="Email"
                  />
                </b-col>
              </b-row>
              <b-row class="mb-3">
                <label for="inputPassword3" class="col-3 col-form-label"
                >Password</label
                >
                <b-col cols="9">
                  <b-form-input
                      type="password"
                      id="inputPassword3"
                      placeholder="Password"
                  />
                </b-col>
              </b-row>
              <b-row class="mb-3">
                <label for="inputPassword5" class="col-3 col-form-label"
                >Re Password</label
                >
                <b-col cols="9">
                  <b-form-input
                      type="password"
                      id="inputPassword5"
                      placeholder="Retype Password"
                  />
                </b-col>
              </b-row>
              <b-row class="mb-3 justify-content-end">
                <b-col cols="9">
                  <b-form-checkbox id="checkmeout"
                  >Check me out !
                  </b-form-checkbox
                  >
                </b-col>
              </b-row>
              <b-row class="justify-content-end">
                <b-col cols="9">
                  <b-button variant="info" type="submit">Sign in</b-button>
                </b-col>
              </b-row>
            </b-form>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <!-- Inline Form -->
    <b-row>
      <b-col md="12">

        <CustomSyntax title="Inline Form">
          <template v-slot:sub-text>
            Use the <code>.row-cols-lg-auto</code>, <code>.g-3</code> &
            <code>.align-items-center</code> class to display a series of
            labels, form controls, and buttons on a single horizontal row.
            Form controls within inline forms vary slightly from their default
            states. Controls only appear inline in viewports that are at least
            576px wide to account for narrow viewports on mobile devices.
          </template>
          <template v-slot:preview>
            <b-form class="row row-cols-lg-auto g-3 align-items-center">
              <b-col cols="12">
                <label for="staticEmail2" class="visually-hidden">Email</label>
                <b-form-input
                    type="text"
                    :readonly="true"
                    :plaintext="true"
                    id="staticEmail2"
                    placeholder="email@example.com"
                />
              </b-col>
              <b-col cols="12">
                <label for="inputPassword2" class="visually-hidden"
                >Password</label
                >
                <b-form-input
                    type="password"
                    id="inputPassword2"
                    placeholder="Password"
                />
              </b-col>
              <b-col cols="12">
                <b-button variant="primary" type="submit">
                  Confirm identity
                </b-button>
              </b-col>
            </b-form>

            <h6 class="fs-13 mt-3">Auto-sizing</h6>
            <b-form>
              <b-row class="gy-2 gx-2 align-items-center">
                <b-col class="col-auto">
                  <label class="visually-hidden" for="inlineFormInput"
                  >Name</label
                  >
                  <b-form-input
                      type="text"
                      class="mb-2"
                      id="inlineFormInput"
                      placeholder="Jane Doe"
                  />
                </b-col>
                <b-col class="col-auto">
                  <label class="visually-hidden" for="inlineFormInputGroup"
                  >Username</label
                  >
                  <b-input-group prepend="@" class="input-group mb-2">
                    <b-form-input
                        type="text"
                        id="inlineFormInputGroup"
                        placeholder="Username"
                    />
                  </b-input-group>
                </b-col>
                <b-col class="col-auto">
                  <div class="mb-2">
                    <b-form-checkbox id="autoSizingCheck"
                    >Remember me
                    </b-form-checkbox
                    >
                  </div>
                </b-col>
                <b-col class="col-auto">
                  <b-button variant="primary" type="submit" class="mb-2">
                    Submit
                  </b-button>
                </b-col>
              </b-row>
            </b-form>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">
        <CustomSyntax title="Horizontal form label sizing">
          <template v-slot:sub-text>
            Be sure to use <code>.col-form-label-sm</code> or
            <code>.col-form-label-lg</code> to your
            <code>&lt;label&gt;</code>s or <code>&lt;legend&gt;</code>s to
            correctly follow the size of <code>.form-control-lg</code> and
            <code>.form-control-sm</code>.
          </template>
          <template v-slot:preview>
            <b-form>
              <b-row class="mb-2">
                <label
                    for="colFormLabelSm"
                    class="col-sm-2 col-form-label col-form-label-sm"
                >Email</label
                >
                <b-col sm="10">
                  <b-form-input
                      type="email"
                      class="form-control-sm"
                      id="colFormLabelSm"
                      placeholder="col-form-label-sm"
                  />
                </b-col>
              </b-row>

              <b-row class="mb-2">
                <label for="colFormLabel" class="col-sm-2 col-form-label"
                >Email</label
                >
                <b-col sm="10">
                  <b-form-input
                      type="email"
                      id="colFormLabel"
                      placeholder="col-form-label"
                  />
                </b-col>
              </b-row>

              <b-row>
                <label
                    for="colFormLabelLg"
                    class="col-sm-2 col-form-label col-form-label-lg"
                >Email</label
                >
                <b-col sm="10">
                  <b-form-input
                      type="email"
                      class="form-control-lg"
                      id="colFormLabelLg"
                      placeholder="col-form-label-lg"
                  />
                </b-col>
              </b-row>
            </b-form>
          </template>
        </CustomSyntax>
      </b-col>
    </b-row>

    <!-- Form row -->
    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Form Row">
          <template v-slot:sub-text>
            By adding <code>.row</code> & <code>.g-2</code>, you can have
            control over the gutter width in as well the inline as block
            direction.
          </template>
          <template v-slot:preview>
            <b-form>
              <b-row class="g-2">
                <b-col md="6" class="mb-3">
                  <b-form-group label="Email" label-for="inputEmail4">
                    <b-form-input
                        type="email"
                        class="form-control"
                        id="inputEmail4"
                        placeholder="Email"
                    />
                  </b-form-group>
                </b-col>
                <b-col md="6" class="mb-3">
                  <b-form-group label="Password" label-for="inputPassword4">
                    <b-form-input
                        type="password"
                        class="form-control"
                        id="inputPassword4"
                        placeholder="Password"
                    />
                  </b-form-group>
                </b-col>
              </b-row>

              <b-form-group
                  label="Address"
                  label-for="inputAddress"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="inputAddress"
                    placeholder="1234 Main St"
                />
              </b-form-group>

              <b-form-group
                  label="Address 2"
                  label-for="inputAddress2"
                  class="mb-3"
              >
                <b-form-input
                    type="text"
                    id="inputAddress2"
                    placeholder="Apartment, studio, or floor"
                />
              </b-form-group>

              <b-row class="g-2">
                <b-col md="6" class="mb-3">
                  <b-form-group label="City" label-for="inputCity">
                    <b-form-input type="text" id="inputCity"/>
                  </b-form-group>
                </b-col>
                <b-col md="4" class="mb-3">
                  <b-form-group label="State" label-for="inputState">
                    <b-form-select
                        v-model="selected3"
                        :options="options3"
                        id="inputState"
                    >
                    </b-form-select>
                  </b-form-group>
                </b-col>
                <b-col md="2" class="mb-3">
                  <b-form-group label="Zip" label-for="inputZip"></b-form-group>
                  <b-form-input type="text" id="inputZip"/>
                </b-col>
              </b-row>

              <div class="mb-2">
                <b-form-checkbox id="customCheck11"
                >Check this custom checkbox
                </b-form-checkbox
                >
              </div>
              <b-button variant="primary" type="submit">Sign in</b-button>
            </b-form>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {CustomSyntax, Layout, Breadcrumb},
  data() {
    return {
      title: 'Form Elements',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Forms',
          href: '/',
        },
        {
          text: 'Form Elements',
          active: true,
        },
      ],

      checked: true,
      selected1: 1,
      selected2: null,
      selected3: null,
      selected4: null,
      options1: [
        {value: 1, text: 1},
        {value: 2, text: 2},
        {value: 3, text: 3},
        {value: 4, text: 4},
        {value: 5, text: 5},
      ],
      options2: [
        {value: null, text: "Open this select menu"},
        {value: 1, text: "One"},
        {value: 2, text: "Two"},
        {value: 3, text: "Three"},
      ],
      options3: [
        {value: null, text: "Choose..."},
        {value: 1, text: "One"},
        {value: 2, text: "Two"},
        {value: 3, text: "Three"},
      ],
      options4: [
        {value: null, text: "Choose"},
        {value: 1, text: "Option 1"},
        {value: 2, text: "Option 2"},
        {value: 3, text: "Option 3"},
      ],
    };
  },

};
</script>
