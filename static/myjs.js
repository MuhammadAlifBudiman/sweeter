/**
 * Posts a comment to the server and reloads the page upon success.
 */
function post() {
  // Get the value of the textarea where the user writes their comment
  let comment = $("#textarea-post").val();
  // Get the current date and time in ISO format
  let today = new Date().toISOString();
  // Send the comment and date to the server via a POST request
  $.ajax({
    type: "POST",
    url: "/posting",
    data: {
      comment_give: comment, // The comment text
      date_give: today, // The current date and time
    },
    success: function (response) {
      // Close the modal and reload the page upon successful posting
      $("#modal-post").removeClass("is-active");
      window.location.reload();
    },
  });
}

/**
 * Fetches posts from the server and displays them in the UI.
 * @param {string} username - The username to filter posts by (optional).
 */
function get_posts(username) {
  // Default to an empty string if no username is provided
  if (username == undefined) {
    username = "";
  }

  // Clear the post box before appending new posts
  $("#post-box").empty();
  // Send a GET request to fetch posts
  $.ajax({
    type: "GET",
    url: `/get_posts?username_give=${username}`, // Include the username in the query string
    data: {},
    success: function (response) {
      if (response["result"] === "success") {
        let posts = response["posts"]; // Array of posts from the server
        for (let i = 0; i < posts.length; i++) {
          let post = posts[i];
          let time_post = new Date(post["date"]); // Convert the post date to a Date object
          let time_before = time2str(time_post); // Format the time difference
          // Determine the appropriate CSS classes for like icons
          let class_heart = post["heart_by_me"] ? "fa-heart" : "fa-heart-o";
          let class_star = post["star_by_me"] ? "fa-star" : "fa-star-o";
          let class_thumbsup = post["thumbsup_by_me"]
            ? "fa-thumbs-up"
            : "fa-thumbs-o-up";
          // Create the HTML template for a post
          let html_temp = `
            <div class="box" id="${post["_id"]}">
                <article class="media">
                    <div class="media-left">
                        <a class="image is-64x64" href="/user/${
                          post["username"]
                        }">
                            <img class="is-rounded" src="/static/${
                              post["profile_pic_real"]
                            }"
                                  alt="Image">
                        </a>
                    </div>
                    <div class="media-content">
                        <div class="content">
                            <p>
                                <strong>${
                                  post["profile_name"]
                                }</strong> <small>@${
            post["username"]
          }</small> <small>${time_before}</small>
                                <br>
                                ${post["comment"]}
                            </p>
                        </div>
                        <nav class="level is-mobile">
                            <div class="level-left">
                                <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${
                                  post["_id"]
                                }', 'heart')">
                                    <span class="icon is-small"><i class="fa ${class_heart}"
                                    aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(
                                      post["count_heart"]
                                    )}</span>
                                </a>
                                <a class="level-item is-sparta" aria-label="star" onclick="toggle_star('${
                                  post["_id"]
                                }', 'star')">
                                    <span class="icon is-small"><i class="fa ${class_star}"
                                    aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(
                                      post["count_star"]
                                    )}</span>
                                </a>
                                <a class="level-item is-sparta" aria-label="thumbsup" onclick="toggle_thumbsup('${
                                  post["_id"]
                                }', 'thumbsup')">
                                    <span class="icon is-small"><i class="fa ${class_thumbsup}"
                                    aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(
                                      post["count_thumbsup"]
                                    )}</span>
                                </a>
                            </div>

                        </nav>
                    </div>
                </article>
              </div>`;
          // Append the post to the post box
          $("#post-box").append(html_temp);
        }
      }
    },
  });
}

/**
 * Converts a date to a human-readable time difference string.
 * @param {Date} date - The date to convert.
 * @returns {string} - The formatted time difference.
 */
function time2str(date) {
  let today = new Date();
  let time = (today - date) / 1000 / 60; // Calculate the difference in minutes

  if (time < 60) {
    return parseInt(time) + " minutes ago"; // Less than an hour
  }
  time = time / 60; // Convert to hours
  if (time < 24) {
    return parseInt(time) + " hours ago"; // Less than a day
  }
  time = time / 24; // Convert to days
  if (time < 7) {
    return parseInt(time) + " days ago"; // Less than a week
  }
  // Return the date in YYYY.MM.DD format
  return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`;
}

/**
 * Toggles the like status of a post.
 * @param {string} post_id - The ID of the post.
 * @param {string} type - The type of like (e.g., "heart").
 */
function toggle_like(post_id, type) {
  console.log(post_id, type); // Log the action for debugging
  let $a_like = $(`#${post_id} a[aria-label='heart']`); // Select the like button
  let $i_like = $a_like.find("i"); // Select the icon inside the button
  if ($i_like.hasClass("fa-heart")) {
    // If the post is already liked
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id, // Post ID
        type_give: type, // Like type
        action_give: "unlike", // Action to unlike
      },
      success: function (response) {
        console.log("unlike"); // Log the action
        $i_like.addClass("fa-heart-o").removeClass("fa-heart"); // Update the icon
        $a_like.find("span.like-num").text(num2str(response["count"])); // Update the like count
      },
    });
  } else {
    // If the post is not liked
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id, // Post ID
        type_give: type, // Like type
        action_give: "like", // Action to like
      },
      success: function (response) {
        console.log("like"); // Log the action
        $i_like.addClass("fa-heart").removeClass("fa-heart-o"); // Update the icon
        $a_like.find("span.like-num").text(num2str(response["count"])); // Update the like count
      },
    });
  }
}

/**
 * Toggles the star status of a post.
 * @param {string} post_id - The ID of the post.
 * @param {string} type - The type of star (e.g., "star").
 */
function toggle_star(post_id, type) {
  console.log(post_id, type); // Log the action for debugging
  let $a_like = $(`#${post_id} a[aria-label='star']`); // Select the star button
  let $i_like = $a_like.find("i"); // Select the icon inside the button
  if ($i_like.hasClass("fa-star")) {
    // If the post is already starred
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id, // Post ID
        type_give: type, // Star type
        action_give: "unlike", // Action to unstar
      },
      success: function (response) {
        console.log("unlike"); // Log the action
        $i_like.addClass("fa-star-o").removeClass("fa-star"); // Update the icon
        $a_like.find("span.like-num").text(num2str(response["count"])); // Update the star count
      },
    });
  } else {
    // If the post is not starred
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id, // Post ID
        type_give: type, // Star type
        action_give: "like", // Action to star
      },
      success: function (response) {
        console.log("like"); // Log the action
        $i_like.addClass("fa-star").removeClass("fa-star-o"); // Update the icon
        $a_like.find("span.like-num").text(num2str(response["count"])); // Update the star count
      },
    });
  }
}

/**
 * Toggles the thumbs-up status of a post.
 * @param {string} post_id - The ID of the post.
 * @param {string} type - The type of thumbs-up (e.g., "thumbsup").
 */
function toggle_thumbsup(post_id, type) {
  console.log(post_id, type); // Log the action for debugging
  let $a_like = $(`#${post_id} a[aria-label='thumbsup']`); // Select the thumbs-up button
  let $i_like = $a_like.find("i"); // Select the icon inside the button
  if ($i_like.hasClass("fa-thumbs-up")) {
    // If the post is already thumbs-upped
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id, // Post ID
        type_give: type, // Thumbs-up type
        action_give: "unlike", // Action to remove thumbs-up
      },
      success: function (response) {
        console.log("unlike"); // Log the action
        $i_like.addClass("fa-thumbs-o-up").removeClass("fa-thumbs-up"); // Update the icon
        $a_like.find("span.like-num").text(num2str(response["count"])); // Update the thumbs-up count
      },
    });
  } else {
    // If the post is not thumbs-upped
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id, // Post ID
        type_give: type, // Thumbs-up type
        action_give: "like", // Action to thumbs-up
      },
      success: function (response) {
        console.log("like"); // Log the action
        $i_like.addClass("fa-thumbs-up").removeClass("fa-thumbs-o-up"); // Update the icon
        $a_like.find("span.like-num").text(num2str(response["count"])); // Update the thumbs-up count
      },
    });
  }
}

/**
 * Converts a number to a human-readable string.
 * @param {number} count - The number to convert.
 * @returns {string} - The formatted string.
 */
function num2str(count) {
  if (count > 10000) {
    return parseInt(count / 1000) + "k"; // Convert to thousands if greater than 10,000
  }
  if (count > 500) {
    return parseInt(count / 100) / 10 + "k"; // Convert to thousands with one decimal if greater than 500
  }
  if (count == 0) {
    return ""; // Return an empty string if the count is zero
  }
  return count; // Return the count as is
}
