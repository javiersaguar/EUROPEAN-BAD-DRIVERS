import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { readFileSync } from 'node:fs'
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
  material: 'Daños materiales · Europa',
  persons: 'Personas y sexo',
  circumstances: 'Tipos de accidente',
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

test('settled claims restore correctly and export their own basis without exposure', async ({
  page,
}) => {
  await page.goto('./?page=material')
  await page.getByLabel('Base de reclamaciones').selectOption('settled')
  await page.getByLabel('Tipo de reclamación').selectOption('Daños materiales a terceros')
  await page.getByLabel('Año histórico').selectOption('2019')
  await page.reload()
  await expect(page.getByLabel('Tipo de reclamación')).toHaveValue('Daños materiales a terceros')
  await expect(
    page.getByRole('heading', { name: 'Frecuencia con exposición compatible' }),
  ).toHaveCount(0)
  await page.locator('.export').first().locator('summary').click()
  const pending = page.waitForEvent('download')
  await page.getByRole('button', { name: /^CSV ·/ }).click()
  const result = await pending
  const text = readFileSync((await result.path())!, 'utf8')
  expect(text).toContain('settlement_year')
  expect(text).toContain('Daños materiales a terceros')
  expect(text).not.toContain('earned_policies_all')
  expect(text).toContain('centralbank.ie')
})

test('absent bicycle cells stay absent in charts and their CSV export', async ({ page }) => {
  await page.goto('./?page=persons&year=2024&user=Bicicleta&zone=Urbana')
  await expect(page.locator('.stats').first()).toContainText('Sin dato')
  await expect(
    page.getByText('1 celda sin dato en esta selección.', { exact: false }),
  ).toBeVisible()
  await page.getByLabel('Sexo registrado', { exact: true }).selectOption('F')
  await page.reload()
  await expect(page.getByLabel('Sexo registrado', { exact: true })).toHaveValue('F')
  await page.locator('.export').first().locator('summary').click()
  const pending = page.waitForEvent('download')
  await page.getByRole('button', { name: /^CSV ·/ }).click()
  const text = readFileSync((await (await pending).path())!, 'utf8')
  expect(text).toContain('Mujeres')
  expect(text).toContain('"F","","Mujeres"')
  expect(text).toContain('dgt.es')
})

test('unknown sex has counts without an invented population rate', async ({ page }) => {
  await page.goto('./?page=persons&sex=UNK&euRole=DRIV&historyYear=2023')
  await expect(page.getByLabel('Año europeo por sexo')).toHaveValue('2023')
  await expect(page.locator('.stat').filter({ hasText: 'Tasa poblacional europea' })).toContainText(
    'Sin dato',
  )
  await expect(
    page.locator('.stat').filter({ hasText: 'Celdas con tasa disponible' }),
  ).toContainText('0 / 27')
  await expect(
    page.getByRole('heading', { name: 'Recuentos europeos, incluido sexo desconocido' }),
  ).toBeVisible()
})

test('conditional severity and vehicle-age filters have usable table alternatives', async ({
  page,
}) => {
  await page.goto('./?page=circumstances&zone=Interurbana&vehicle=Turismo&year=2023')
  await expect(page.getByLabel('Vehículos en el análisis de antigüedad')).toHaveValue('Turismo')
  await page.locator('.evidence-table').nth(1).locator('summary').click()
  await expect(page.getByRole('columnheader', { name: 'Wilson inferior' })).toBeVisible()
  await expect(page.getByRole('columnheader', { name: 'Denominador', exact: true })).toBeVisible()
  await page.getByLabel('Zona del accidente').selectOption('Urbana')
  await page.reload()
  await expect(page.getByLabel('Zona del accidente')).toHaveValue('Urbana')
})
