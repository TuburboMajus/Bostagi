// Function to load YAML translation file
async function loadTranslations(page, language = 'en') {
  try {
    // Determine the path to the translation file
    const translationFile = `/static/js/dictionaries/${page}.yml`;
    
    // Fetch the YAML file
    const response = await fetch(translationFile);
    if (!response.ok) {
      throw new Error(`Failed to load translations: ${response.status}`);
    }
    
    const yamlText = await response.text();
    
    // Parse YAML (using js-yaml library)
    const parsedYaml = jsyaml.load(yamlText);
    
    // Make the translations available globally
    dictionary = parsedYaml[language] || {};
    console.log(`Translations loaded for language: ${language}`);
    return dictionary;
  } catch (error) {
    console.error('Error loading translations:', error);
    // Fallback to empty dictionary
    return {};
  }
}