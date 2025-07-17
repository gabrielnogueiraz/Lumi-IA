console.log('Testando importação do TaskAssistant...')

import { TaskAssistant } from './taskAssistant'

console.log('TaskAssistant importado:', TaskAssistant)
console.log('Tipo:', typeof TaskAssistant)

const instance = new TaskAssistant()
console.log('Instância criada:', instance)
