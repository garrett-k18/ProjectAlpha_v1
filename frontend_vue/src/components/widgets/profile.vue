<template>
  <span class="float-start m-2 me-4">
    <img
      :src="image"
      style="height: 100px"
      alt=""
      class="rounded-circle img-thumbnail"
    />
  </span>
  <div class="">
    <h4  :class="`mt-1 mb-1 text-${textColor}`">{{ name }}</h4>
    <p :class="`font-13 text-${textColor}-50`">{{ role }}</p>

    <ul :class="`mb-0 list-inline text-${textColor}`">
      <li class="list-inline-item me-3">
        <h5 class="mb-1">$ {{ revenue }}</h5>
        <p :class="`mb-0 font-13 text-${textColor}`">Total Revenue</p>
      </li>
      <li class="list-inline-item">
        <h5 class="mb-1">{{ orders }}</h5>
        <p :class="`mb-0 font-13 text-${textColor}`">Number of Orders</p>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
/**
 * Profile-widget component
 * 1. User may specify the image
 * 2. User may specify the name
 * 3. User may specify the role
 * 4. User may specify the total revenue
 * 5. User may specify the total orders
 * 6. User may specify the text color of widget while using in another component. Ex. black, white etc.
 */
export default {
  props: {
    image: { type: Image },
    name: {
      type: String,
      require: true,
    },
    role: {
      type: String,
    },
    revenue: {
      type: String,
      require: true,
    },
    orders: {
      type: Number,
      require: true,
    },
    textColor: {
      type: String,
      default: 'white',
    },
  },
};
</script>
