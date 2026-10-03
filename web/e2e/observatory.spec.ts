import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
const pages = {
  overview: 'Panorama',
  territories: 'Territorios',
  profile: 'Ficha provincial',
  compare: 'Comparar',
  insurance: 'Golpes de chapa',
  trends: 'Series históricas',
  europe: 'Europa',
  laboratory: 'Laboratorio',
  models: 'Modelos',
  sources: 'Fuentes',
}
for (const [key, name] of Object.entries(pages))
  test(`${name}: data, reflow and WCAG AA`, async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto(`./?page=${key}`)
    await expect(page.getByRole('heading', { name, exact: true, level: 1 })).toBeVisible()
    await expect(page.getByText('Cargando la publicación verificada…')).toBeHidden()
    await expect(
      page.getByRole('heading', { name: 'La publicación no está disponible' }),
    ).toBeHidden()
    // Map fetched separately; wait for its province controls before contrast audit.
    if (['overview', 'territories'].includes(key))
      await expect(page.getByRole('button', { name: /Araba.*Abrir ficha/ })).toBeVisible()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze()
    expect(
      results.violations.map((v) => ({
        id: v.id,
        description: v.description,
        nodes: v.nodes.map((n) => n.target),
      })),
    ).toEqual([])
    expect(errors).toEqual([])
  })
test('filters restore across reload and browser history', async ({ page }) => {
  await page.goto('./?page=territories&year=2023&denominator=registered_vehicles')
  await page.getByLabel('Indicador', { exact: true }).selectOption('fatalities')
  await page.getByLabel('Año', { exact: true }).selectOption('2022')
  await page.reload()
  await expect(page.getByLabel('Indicador', { exact: true })).toHaveValue('fatalities')
  await expect(page.getByLabel('Año', { exact: true })).toHaveValue('2022')
  await expect(page.getByLabel('Denominador', { exact: true })).toHaveValue('registered_vehicles')
  await page.getByLabel('Año', { exact: true }).selectOption('2024')
  await page.goBack()
  await expect(page.getByLabel('Año', { exact: true })).toHaveValue('2022')
})
test('map is operable by keyboard and opens the matching province', async ({ page }) => {
  await page.goto('./')
  const province = page.getByRole('button', { name: /Madrid:.*Abrir ficha/ })
  await province.focus()
  await province.press('Enter')
  await expect(page.getByRole('heading', { name: 'Ficha provincial', level: 1 })).toBeVisible()
  await expect(page.getByLabel('Provincia', { exact: true })).toHaveValue('28')
})
test('insurance selection and actual downloads', async ({ page }) => {
  await page.goto('./?page=insurance')
  await page.getByLabel('Selección publicada').selectOption('lower')
  await expect(page.getByRole('cell', { name: 'Orihuela', exact: true })).toBeVisible()
  await expect(page.getByLabel('Año', { exact: true })).toHaveCount(0)
  for (const format of ['CSV', 'PDF', 'SVG', 'PNG']) {
    await page.locator('.export').first().locator('summary').click()
    const pending = page.waitForEvent('download')
    await page.getByRole('button', { name: new RegExp(`^${format} ·`) }).click()
    const download = await pending
    expect(download.suggestedFilename()).toMatch(new RegExp(`\\.${format.toLowerCase()}$`))
    expect(await download.failure()).toBeNull()
  }
})
test('zero weights are an explicit state', async ({ page }) => {
  await page.goto('./?page=laboratory&weights=0,0,0,0')
  await expect(page.getByRole('alert')).toHaveText(
    'Activa al menos un peso para calcular el índice.',
  )
})
test('failed data request can be retried', async ({ page }) => {
  await page.route('**/data/observatory.json', (route) => route.abort())
  await page.goto('./')
  await expect(page.getByRole('alert')).toContainText('La publicación no está disponible')
  await page.unroute('**/data/observatory.json')
  await page.getByRole('button', { name: 'Reintentar' }).click()
  await expect(page.getByText('101.996', { exact: true })).toBeVisible()
})
test('mobile navigation has focus and closes with escape', async ({ page, isMobile }) => {
  test.skip(!isMobile)
  await page.goto('./')
  await page.getByRole('button', { name: 'Abrir navegación' }).click()
  await expect(page.getByRole('button', { name: 'Cerrar menú' })).toBeFocused()
  await page.getByRole('button', { name: 'Cerrar menú' }).press('Escape')
  await expect(page.getByRole('button', { name: 'Abrir navegación' })).toBeFocused()
})
