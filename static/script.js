const content = `${window.location.href} \n\n ${document.body.innerText}`;
const link = window.location.href;
// Function to copy content
function copyContent(content) {
    // Create a temporary input element
    let tempInput = document.createElement("input");
    // Set its value to the content
    tempInput.value = content;
    // Append it to the body
    document.body.appendChild(tempInput);
    // Select its content
    tempInput.select();
    // Copy the content to the clipboard
    document.execCommand("copy");
    // Remove the input element
    document.body.removeChild(tempInput);
    // Show a success message
    alert("Konten berhasil disalin");
  }
  
  // Function to share on Facebook
  function shareFacebook(content) {
    // Open a new window to share the content on Facebook
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(content)}&url=${encodeURIComponent(link)}`);
  }
  
  // Function to share on Twitter
  function shareTwitter(content) {
    // Open a new window to share the content on Twitter
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(content)}&url=${encodeURIComponent(link)}`);
  }
  
  // Function to share on WhatsApp
  function shareWhatsApp(content) {
    // Open a new window to share the content on WhatsApp
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(content)}&url=${encodeURIComponent(link)}`);
  }
  
  // Function to share on Instagram
  function shareInstagram(content) {
    // Open a new window to share the content on Instagram
    window.open(`https://www.instagram.com/share?url=${encodeURIComponent(content)}&url=${encodeURIComponent(link)}`);
  }
  
  const contentBlockquote = document.querySelector("blockquote").innerText;
  
  // Tombol Share ke Facebook
document.getElementById("share-facebook").addEventListener("click", function() {
    shareFacebook(contentBlockquote);
  });
  
  // Tombol Share ke Twitter
  document.getElementById("share-twitter").addEventListener("click", function() {
    shareTwitter(contentBlockquote);
  });
  
  // Tombol Share ke WhatsApp
  document.getElementById("share-whatsapp").addEventListener("click", function() {
    shareWhatsApp(contentBlockquote);
  });
  
  // Tombol Share ke Instagram
  document.getElementById("share-instagram").addEventListener("click", function() {
    shareInstagram(contentBlockquote);
  });
  
  // Tombol Copy Link
  document.getElementById("copy-link").addEventListener("click", function() {
    copyContent(contentBlockquote);
  });