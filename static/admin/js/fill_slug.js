function slugify(str) {
    return String(str)
      .normalize('NFKD') // split accented characters into their base characters and diacritical marks
      .replace(/[\u0300-\u036f]/g, '') // remove all the accents, which happen to be all in the \u03xx UNICODE block.
      .trim() // trim leading or trailing whitespace
      .toLowerCase() // convert to lowercase
      .replace(/[^a-z0-9 -]/g, '') // remove non-alphanumeric characters
      .replace(/\s+/g, '-') // replace spaces with hyphens
      .replace(/-+/g, '-'); // remove consecutive hyphens
  }

  document.addEventListener("DOMContentLoaded", function () {
    const parentSelect = document.querySelector("#id_parent_category");
    const nameInput = document.querySelector("#id_name");
    const slugInput = document.querySelector("#id_slug");
  
    if (!nameInput || !slugInput) return;
  
    const updateSlug = () => {
      const selectedOption = parentSelect ? parentSelect.querySelector("option:checked") : null;
      const baseValue = selectedOption ? `${selectedOption.innerText}${nameInput.value}` : nameInput.value;
      slugInput.value = slugify(baseValue);
    };
  
    nameInput.addEventListener("input", updateSlug);
  
    if (parentSelect) {
      parentSelect.addEventListener("change", updateSlug);
    }
  });
  