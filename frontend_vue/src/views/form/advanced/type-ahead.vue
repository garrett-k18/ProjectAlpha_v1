<template>
  <CustomSyntax title="Typeahead">
    <template v-slot:sub-text>
      Typeahead.js is a fast and fully-featured autocomplete library.
    </template>
    <template v-slot:preview>
      <b-row>
        <b-col lg="6">
          <b-form-group label="The Basics" class="mb-3">
            <b-form-input
                type="text"
                data-provide="typeahead"
                id="the-basics"
                placeholder="Basic Example"
            />
          </b-form-group>
        </b-col>

        <b-col lg="6" class="mt-3 mt-lg-0">
          <b-form-group label="Bloodhound (Suggestion Engine)" class="mb-3">
            <b-form-input
                id="bloodhound"
                type="text"
                placeholder="States of USA"
            />
          </b-form-group>
        </b-col>
      </b-row>

      <b-row>
        <b-col lg="6">
          <b-form-group label="Prefetch" class="mb-3">
            <b-form-input
                type="text"
                data-provide="typeahead"
                id="prefetch"
                placeholder="States of USA"
            />
          </b-form-group>
        </b-col>

        <b-col lg="6" class="mt-3 mt-lg-0">
          <b-form-group label="Remote" class="mb-3">
            <b-form-input
                type="text"
                data-provide="typeahead"
                id="remote"
                placeholder="States of USA"
            />
          </b-form-group>
        </b-col>
      </b-row>

      <b-row>
        <b-col lg="6">
          <b-form-group label="Custom Templates" class="mb-3">
            <b-form-input
                id="custom-templates"
                type="text"
                placeholder="States of USA"
            />
          </b-form-group>
        </b-col>

        <b-col lg="6" class="mt-3 mt-lg-0">
          <b-form-group label="Default Suggestions" class="mb-3">
            <b-form-input
                type="text"
                data-provide="typeahead"
                id="default-suggestions"
            />
          </b-form-group>
        </b-col>
      </b-row>

      <b-row>
        <b-col lg="6">
          <b-form-group label="Multiple Datasets" class="mb-0">
            <b-form-input
                type="text"
                data-provide="typeahead"
                id="multiple-datasets"
            />
          </b-form-group>
        </b-col>
      </b-row>
    </template>
  </CustomSyntax>
</template>

<script lang="ts">
import "typeahead.js/dist/typeahead.bundle.min.js";
import Bloodhound from "typeahead.js/dist/bloodhound.js";
import Handlebars from "handlebars";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {CustomSyntax},
  mounted() {
    let substringMatcher = function (strs: any) {
      return function findMatches(q: string, cb: any) {
        let matches: any, substringRegex;

        // an array that will be populated with substring matches
        matches = [];

        // regex used to determine if a string contains the substring `q`
        let substrRegex = new RegExp(q, "i");

        // iterate through the pool of strings and for any string that
        // contains the substring `q`, add it to the `matches` array
        $.each(strs, function (i, str) {
          if (substrRegex.test(str)) {
            matches.push(str);
          }
        });

        cb(matches);
      };
    };

    let states = [
      "Alabama",
      "Alaska",
      "Arizona",
      "Arkansas",
      "California",
      "Colorado",
      "Connecticut",
      "Delaware",
      "Florida",
      "Georgia",
      "Hawaii",
      "Idaho",
      "Illinois",
      "Indiana",
      "Iowa",
      "Kansas",
      "Kentucky",
      "Louisiana",
      "Maine",
      "Maryland",
      "Massachusetts",
      "Michigan",
      "Minnesota",
      "Mississippi",
      "Missouri",
      "Montana",
      "Nebraska",
      "Nevada",
      "New Hampshire",
      "New Jersey",
      "New Mexico",
      "New York",
      "North Carolina",
      "North Dakota",
      "Ohio",
      "Oklahoma",
      "Oregon",
      "Pennsylvania",
      "Rhode Island",
      "South Carolina",
      "South Dakota",
      "Tennessee",
      "Texas",
      "Utah",
      "Vermont",
      "Virginia",
      "Washington",
      "West Virginia",
      "Wisconsin",
      "Wyoming",
    ];

    $("#the-basics").typeahead(
        {
          hint: true,
          highlight: true,
          minLength: 1,
        },
        {
          name: "states",
          source: substringMatcher(states),
        }
    );

    let states1 = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.whitespace,
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      // `states` is an array of state names defined in "The Basics"
      local: states,
    });

    $("#bloodhound").typeahead(
        {
          hint: true,
          highlight: true,
          minLength: 1,
        },
        {
          name: "states",
          source: states1,
        }
    );

    let countries = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.whitespace,
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      // url points to a json file that contains an array of country names, see
      prefetch:
          "https://raw.githubusercontent.com/twitter/typeahead.js/gh-pages/data/countries.json",
    });

    // passing in `null` for the `options` arguments will result in the default
    // options being used
    $("#prefetch").typeahead(null, {
      name: "countries",
      source: countries,
    });

    let bestPictures = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      prefetch:
          "https://raw.githubusercontent.com/twitter/typeahead.js/gh-pages/data/films/post_1960.json",
      remote: {
        url: "../plugins/typeahead/data/%QUERY.json",
        wildcard: "%QUERY",
      },
    });

    $("#remote").typeahead(null, {
      name: "best-pictures",
      display: "value",
      source: bestPictures,
    });

    let nflTeams = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace("team"),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      identify: function (obj: any) {
        return obj.team;
      },
      prefetch:
          "https://raw.githubusercontent.com/twitter/typeahead.js/gh-pages/data/nfl.json",
    });

    function nflTeamsWithDefaults(q: string, sync: any) {
      if (q === "") {
        sync(
            nflTeams.get("Detroit Lions", "Green Bay Packers", "Chicago Bears")
        );
      } else {
        nflTeams.search(q, sync);
      }
    }

    $("#default-suggestions").typeahead(
        {
          minLength: 0,
          highlight: true,
        },
        {
          name: "nfl-teams",
          display: "team",
          source: nflTeamsWithDefaults,
        }
    );

    let nbaTeams = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace("team"),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      prefetch:
          "https://raw.githubusercontent.com/twitter/typeahead.js/gh-pages/data/nba.json",
    });

    let nhlTeams = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace("team"),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      prefetch:
          "https://raw.githubusercontent.com/twitter/typeahead.js/gh-pages/data/nhl.json",
    });

    $("#multiple-datasets").typeahead(
        {
          highlight: true,
        },
        {
          name: "nba-teams",
          display: "team",
          source: nbaTeams,
          templates: {
            header: '<h5 class="league-name">NBA Teams</h5>',
          },
        },
        {
          name: "nhl-teams",
          display: "team",
          source: nhlTeams,
          templates: {
            header: '<h5 class="league-name">NHL Teams</h5>',
          },
        }
    );

    $("#custom-templates").typeahead(null, {
      name: "best-pictures",
      display: "value",
      source: bestPictures,
      templates: {
        empty: [
          '<div class="typeahead-empty-message">',
          "Unable to find any Best Picture winners that match the current query",
          "</div>",
        ].join("\n"),
        suggestion: Handlebars.compile(
            "<div><strong>{{value}}</strong> - {{year}}</div>"
        ),
      },
    });
  },
};
</script>
