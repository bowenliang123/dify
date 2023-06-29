import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useContext } from 'use-context-selector'
import style from './users.module.css'
import Button from '@/app/components/base/button'
import Dialog from '@/app/components/base/dialog'
import { ToastContext } from '@/app/components/base/toast'
import { addUsers } from '@/service/users'

type AddUsersDialogProps = {
  show: boolean
  onSuccess?: () => void
  onClose?: () => void
}

const AddUsersDialog = ({ show, onSuccess, onClose }: AddUsersDialogProps) => {
  const { notify } = useContext(ToastContext)
  const { t } = useTranslation()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const onCreated = async () => {
    if (!name || !email || !password) {
      notify({ type: 'error', message: '请输入完整用户信息' })
      return false
    }

    const params = { name, email, password }
    const ans: any = await addUsers(params)

    if (onSuccess && ans.result === 'success')
      onSuccess()

    if (ans.result === 'failed')
      notify({ type: 'error', message: ans.message })
  }

  const onClosed = () => {
    setName('')
    setEmail('')
    setPassword('')
    if (onClose)
      onClose()
  }
  return (
    <div>
      <Dialog
        show={show}
        title='新增用户'
        footer={
          <>
            <Button onClick={onClosed}>{t('app.newApp.Cancel')}</Button>
            <Button type="primary" onClick={onCreated}>{t('app.newApp.Create')}</Button>
          </>
        }
      >
        <div className={style.divStyle}>
          <span className={style.labelStyle}>用户名：</span>
          <input onChange={(e) => { setName(e.target.value) }} className='h-10 px-3 text-sm font-normal bg-gray-100 rounded-lg grow' />
        </div>
        <div className={style.divStyle}>
          <span className={style.labelStyle}>邮箱：</span>
          <input id="email" type="email" value={email} onChange={(e) => { setEmail(e.target.value) }} className='h-10 px-3 text-sm font-normal bg-gray-100 rounded-lg grow' />
        </div>
        <div className={style.divStyle}>
          <span className={style.labelStyle}>密码：</span>
          <input id="password" value={password} onChange={(e) => { setPassword(e.target.value) }} className='h-10 px-3 text-sm font-normal bg-gray-100 rounded-lg grow' />
        </div>
      </Dialog>
    </div>
  )
}

export default AddUsersDialog
