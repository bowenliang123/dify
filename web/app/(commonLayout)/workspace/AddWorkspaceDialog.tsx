import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useContext } from 'use-context-selector'
import style from './workspace.module.css'
import Button from '@/app/components/base/button'
import Dialog from '@/app/components/base/dialog'
import { ToastContext } from '@/app/components/base/toast'
import { addWorkspace } from '@/service/workspace'

type AddWorkspaceDialogProps = {
  show: boolean
  onSuccess?: () => void
  onClose?: () => void
}

const AddWorkspaceDialog = ({ show, onSuccess, onClose }: AddWorkspaceDialogProps) => {
  const { notify } = useContext(ToastContext)
  const { t } = useTranslation()
  const [name, setName] = useState('')

  const onCreated = async () => {
    if (!name.trim()) {
      notify({ type: 'error', message: '请输入workspace名称' })
      return false
    }

    const ans: any = await addWorkspace({ name })

    if (onSuccess && ans.result === 'success') {
      onSuccess()
      setName('')
    }

    if (ans.result === 'failed')
      notify({ type: 'error', message: ans.message })
  }

  const onClosed = () => {
    setName('')
    if (onClose)
      onClose()
  }

  return (
    <div>
      <Dialog
        show={show}
        title='新增workspace'
        footer={
          <>
            <Button onClick={onClosed}>{t('app.newApp.Cancel')}</Button>
            <Button type="primary" onClick={onCreated}>{t('app.newApp.Create')}</Button>
          </>
        }
      >
        <div className={style.divStyle}>
          <span className={style.labelStyle}>workspace名称：</span>
          <input onChange={(e) => { setName(e.target.value) }} className='h-10 px-3 text-sm font-normal bg-gray-100 rounded-lg grow' />
        </div>
      </Dialog>
    </div>
  )
}

export default AddWorkspaceDialog
