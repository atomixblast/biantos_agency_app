
document.addEventListener('alpine:init', () => {


    Alpine.data('update_bill', () => ({
        selectedRow: 0,
        currentInput: '',
        addDiscountColumn: true,
        estimateField: '',
        estimateCurrency: '1',
        estimateTVA: 0,
        estimateCA: 0,
        tva: 0,
        ca: 0,
        discount: 0,
        discountType: 'PERCENT',

        mode: 'pending', 
        isSubmitting: false,
        showNotification: false,
        notificationMessage: '',
        articleField: '', 
        qtyField: '', 
        discountField: '', 
        articleReprField: '', 

        orderArticles : [],
        articles : [],  // Will be loaded from database

        estimates : [
            {
                designation: '',
                qty: 0,
                pu: 0,
                discount: 0,
                total: 0,
            },
        ],

        services: [],
        currencies: [],

        init(){
            this.estimateField = document.getElementById('id_bill_contents')

            this.articleField = document.getElementById('add_article_field')
            this.qtyField = document.getElementById('add_qty_field')
            this.discountField = document.getElementById('add_discount_field')
            this.articleReprField = document.getElementById('id_json_repr')

            // Remise sur la commande : valeur initiale fournie par le serveur
            const globalDiscountField = document.getElementById('id_global_discount')
            if (globalDiscountField) {
                this.discount = parseFloat(globalDiscountField.value) || 0
            }
            const globalDiscountTypeField = document.getElementById('id_global_discount_type')
            if (globalDiscountTypeField) {
                this.discountType = globalDiscountTypeField.value || 'PERCENT'
            }

            // Load articles from database
            if(document.getElementById('articles-data')){
                const articlesData = JSON.parse(document.getElementById('articles-data').textContent)
                // Transform to match expected format
                this.articles = articlesData.map(article => ({
                    id: article.id,
                    designation: article.name,
                    pu: article.sale_price,
                    ref: article.ref
                }))
            }

            // Load existing articles for this order
            if(document.getElementById('existing-articles-data')){
                const existingArticlesData = JSON.parse(document.getElementById('existing-articles-data').textContent)
                this.orderArticles = existingArticlesData.map(article => {
                    const subtotal = article.qty * article.pu
                    const discountAmount = subtotal * (article.discount / 100)
                    const total = subtotal - discountAmount
                    
                    return {
                        id: article.id,
                        designation: article.designation,
                        pu: article.pu,
                        qty: article.qty,
                        discount: article.discount,
                        total: total
                    }
                })
                
                // Update the hidden field with existing articles
                this.articleReprField.value = JSON.stringify(this.orderArticles)
            }

            const estimateData = document.getElementById('estimate-data')

            if(document.getElementById('services-data')){
                this.services = JSON.parse(document.getElementById('services-data').textContent)
                this.services_to_choose = this.services
            }

            if(document.getElementById('currencies-data')){
                this.currencies = JSON.parse(document.getElementById('currencies-data').textContent)
            }
            
            if (estimateData){
                const result = JSON.parse(estimateData.textContent)
                this.estimateCA = result.CA
                this.estimateTVA = result.TVA
                this.estimateCurrency = result.currency
                this.estimates = result.estimate_contents
                this.addDiscountColumn = this.estimates.filter(estimate => estimate.discount >0) ? true : false
            }

            this.$watch('mode', (value)=>{
                if(value=='edit'){
                    this.articleField.focus()
                }
            })

            document.addEventListener('keyup', (e)=>{
                if([this.articleField, this.qtyField, this.discountField].includes(document.activeElement) && e.key === 'Enter'){
                    this.addArticleToOrder()
                }
            })

        },

        addArticleToOrder(){
            if (this.articleField.value && this.qtyField.value && this.qtyField.value*1 >0){
                const article = this.articles.filter(article => article.id === this.articleField.value*1)[0]
                const qty = parseFloat(this.qtyField.value) || 0
                const discount = parseFloat(this.discountField.value) || 0
                const pu = article.pu
                
                // Check if article already exists in cart
                const existingArticleIndex = this.orderArticles.findIndex(item => item.id === article.id)
                
                if (existingArticleIndex !== -1) {
                    // Article exists - show warning and don't add
                    this.showWarningMessage(`"${article.designation}" est déjà dans la commande. Supprimez-le d'abord pour le modifier.`)
                    return // Don't add or update
                }
                
                // New article - add to cart
                const subtotal = qty * pu
                const discountAmount = subtotal * (discount / 100)
                const total = subtotal - discountAmount
                
                this.orderArticles.push({
                    id: article.id,
                    designation: article.designation,
                    pu: pu,
                    qty: qty,
                    discount: discount,
                    total: total,
                })
                
                this.articleReprField.value = JSON.stringify(this.orderArticles)
                this.articleField.value = ''
                this.qtyField.value = ''
                this.discountField.value = ''
                this.articleField.focus()
            }
        },

        showWarningMessage(message){
            this.notificationMessage = message
            this.showNotification = true
            setTimeout(() => {
                this.showNotification = false
            }, 8000) // Hide after 8 seconds
        },

        removeArticleToOrder(index){
            this.orderArticles.splice(index, 1)
            this.articleReprField.value = JSON.stringify(this.orderArticles)
            this.articleField.focus()
        },

        get canCreateOrder(){
            return this.orderArticles.length
        },

        // Total après remises par article
        get linesTotal(){
            return this.orderArticles.reduce((sum, article) => sum + article.total, 0)
        },

        // Remise sur toute la commande, appliquée après les remises par article :
        // en % du total des articles, ou en montant FCFA (plafonné au total).
        get globalDiscountAmount(){
            const value = Math.max(parseFloat(this.discount) || 0, 0)
            if (this.discountType === 'AMOUNT') {
                return Math.min(value, this.linesTotal)
            }
            return this.linesTotal * Math.min(value, 100) / 100
        },

        get globalDiscountLabel(){
            if (this.discountType === 'AMOUNT') {
                return 'Remise sur la commande'
            }
            return 'Remise sur la commande (' + (parseFloat(this.discount) || 0) + ' %)'
        },

        get grandTotal(){
            return this.linesTotal - this.globalDiscountAmount
        },

        get grandTotalFormatted(){
            return this.grandTotal.toFixed(2)
        },

        isArticleInCart(articleId){
            return this.orderArticles.some(item => item.id === articleId)
        },



        addRow(index){
            this.estimates.splice(index+1, 0,
                {
                    designation: this.services[0],
                    qty: 0,
                    pu: 0,
                    discount: 0,
                    total: 0,
                }
            )
            window.scroll(0, 8000)
        },

        deleteRow(index){
            this.estimates.splice(index, 1)
        },

        selectRow(index){
            this.selectedRow = index
            console.log('row selected ', this.selectedRow)
        },

        setCurrentInput(index, field){
            this.currentInput = field
            this.selectedRow = index
        },

        updateCurrentInput(e){
            this.estimates[this.selectedRow][this.currentInput] = e.target.value
            this.estimates[this.selectedRow].total = this.estimates[this.selectedRow].qty*this.estimates[this.selectedRow].pu*(
                1 - (this.addDiscountColumn ? this.estimates[this.selectedRow].discount/100 : 0)
            )
        },

        get getTotal(){
            this.estimateField.value = JSON.stringify(this.estimates)
            const totals = this.estimates.map(estimate => estimate.total)
            return totals.reduce((a, c) => a+c,0)*(1-this.discount/100)
        },

        get getTTC(){
            const total = this.getTotal
            const TVA = total*this.tva/100
            return total + TVA + TVA*this.ca/100
        },

        get getTTax(){
            const total = this.getTotal
            const TVA = total*this.tva/100
            return TVA + TVA*this.ca/100
        },

        get printCurrency(){
            return this.currencies[parseInt(this.estimateCurrency)-1].toUpperCase()
        }

    }))


})
