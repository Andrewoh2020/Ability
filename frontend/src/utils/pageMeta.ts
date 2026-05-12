const originalTitle = document.title;
const originalDescription = document.querySelector('meta[name="description"]')?.getAttribute('content') || '';

export function setPageTitle(newTitle: string, mode = 'prefix') {
  if (mode === 'replace') {
    document.title = newTitle;
  } else {
    document.title = `${newTitle} - ${originalTitle}`;
  }
}

export function setPageDescription(description: string) {
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute('content', description);
  } else {
    const meta = document.createElement('meta');
    meta.name = 'description';
    meta.content = description;
    document.head.appendChild(meta);
  }
}

export function resetPageTitle() {
  document.title = originalTitle;
}

export function resetPageDescription() {
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription && originalDescription) {
    metaDescription.setAttribute('content', originalDescription);
  }
}
