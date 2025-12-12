<template>
  <div class="container sm:px-16 px-6 pt-8 max-w-5xl">
    <p v-if="$fetchState.pending">Fetching posts...</p>
    <p v-else-if="$fetchState.error">
      Error while fetching posts: {{ $fetchState.error.message }}
    </p>
    <ul v-else>
      <li v-for="post of posts.items" :key="post.id" class="pb-4">
        <n-link
          :to="`/${post.meta.slug}`"
          class="text-5xl avenir font-bold leading-none text-gray-800 pb-6"
          >{{ post.title }}</n-link
        >
        <p class="date pt-0 pb-4 athelas font-light text-red-400">
          {{ post.date | datify }}
        </p>
      </li>
    </ul>
  </div>
</template>

<script>
import utils from "../components/lib";

export default {
  data() {
    return {
      posts: [],
    };
  },
  head() {
    return {
      title: "Tom Dyson",
      meta: [
        {
          hid: "description",
          name: "description",
          content: "Tom Dyson's blog",
        },
      ],
    };
  },
  async fetch() {
    this.posts = await this.$http.$get(
      `${process.env.baseApiUrl}/pages/?type=blog.BlogPage&fields=title,date&show_in_menus=true`
    );
  },
  filters: {
    datify: utils.datify,
  },
};
</script>

<style scoped>
.athelas {
  font-family: "Source Serif Pro", athelas, georgia, serif;
}
.avenir {
  font-family: "avenir next", avenir, -apple-system, BlinkMacSystemFont,
    "helvetica neue", helvetica, ubuntu, roboto, noto, "segoe ui", arial,
    sans-serif;
}
.date {
  font-size: 1.4rem;
}
</style>